# Código baseado em https://docs.python.org/3.6/library/asyncio-stream.html#tcp-echo-client-using-streams
import asyncio
import argparse
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import padding
import validate_cert
import os
import aes_ctr

# CONSTANTS

conn_port = 8443
max_msg_size = 9999
p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
g = 2
ca_cert = x509.load_pem_x509_certificate(open("MSG_CLI1.crt", "rb").read())
end = 0


# CLIENT


def validate_rsa_signature(rsa_public_key, signature, data):
    try:
        rsa_public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except:
        return False


def mkpair(x, y):
    """ produz uma byte-string contendo o tuplo '(x,y)' ('x' e 'y' são byte-strings) """
    len_x = len(x)
    len_x_bytes = len_x.to_bytes(2, 'little')
    return len_x_bytes + x + y


def unpair(xy):
    """ extrai componentes de um par codificado com 'mkpair' """
    len_x = int.from_bytes(xy[:2], 'little')
    x = xy[2:len_x+2]
    y = xy[len_x+2:]
    return x, y


class Client:
    """ Classe que implementa a funcionalidade de um CLIENTE. """

    def __init__(self, user_data="MSG_CLI1", sckt=None):
        """ Construtor da classe. """
        self.sckt = sckt
        self.msg_cnt = 0
        self.dhprivate_key = dh.DHParameterNumbers(
            p, g).parameters().generate_private_key()
        self.rsaprivate_key = None
        self.shared_key = None
        file = f"{user_data}.p12"
        with open(file, "rb") as p12_file:
            (self.rsaprivate_key, self.cert, _) = serialization.pkcs12.load_key_and_certificates(
                p12_file.read(),
                password=None,
            )
        # pkcs12 load_key_and_certificates , ficheiro e a passe None
        # passe server 1234

    def dh_key(self):
        self.msg_cnt += 1

        publicKey = self.dhprivate_key.public_key()
        pem = publicKey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem

    def process_server_info(self, server_info):
        self.msg_cnt += 1

        server_dh_pub = serialization.load_pem_public_key(
            unpair(server_info)[0])
        signature, cert_name = unpair(unpair(server_info)[1])
        cert_name = cert_name.decode()

        # Verifica o certificado

        cert = x509.load_pem_x509_certificate(cert_name.encode())

        if not validate_cert.valida_cert(cert, "Server"):
            print("✗ Certicate is not valid")
            return None
        print("✓ Certificate is valid")

        server_rsa_public_key = cert.public_key()

        # Verifica a assinatura

        dh_pair = mkpair(
            server_dh_pub.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ),
            self.dhprivate_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo)
        )

        if not validate_rsa_signature(server_rsa_public_key, signature, dh_pair):
            print("✗ Signature is not valid")
            return None
        print("✓ Signature is valid")

        # Gera a chave partilhada

        shared_key = self.dhprivate_key.exchange(server_dh_pub)
        self.shared_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data',
        ).derive(shared_key)

        print("> Shared key generated.")

        # Devolve ao servidor a chave pública, certificado e assinatura

        signature = self.rsaprivate_key.sign(
            mkpair(
                self.dhprivate_key.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ),
                server_dh_pub.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            ),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        pair1 = mkpair(signature, self.cert.public_bytes(
            encoding=serialization.Encoding.PEM))
        pair2 = mkpair(
            self.dhprivate_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo),
            pair1
        )

        return pair2


# MAIN FUNCTIONALITY


def help():
    """
    Print the help menu.
    """
    print("The following commands are available:")
    print()
    print("-user <FNAME> -- option argument which specifies the user's data file. The default is userdata.p12")
    print("send <UID> <SUBJECT> -- sends a message with subject <SUBJECT> to the user with an identifier <UID>. The max size is 1000 bytes.")
    print("askqueue -- asks the server for the non read messages in the queue for the user.")
    print("getmsg <NUM> -- gets the message with the number <NUM> from the queue.")
    print("help -- prints this help message.")
    print()
    return None


async def tcp_echo_client():
    # parse arguments
    parser = argparse.ArgumentParser(description='Client for TCP Echo Server')
    parser.add_argument('-user', dest='userdata', default='MSG_CLI1',
                        help='Specify user data file (default: userdata.p12)')
    parser.add_argument('command', choices=[
                        'send', 'askqueue', 'getmsg', 'help'], help='Command to execute')
    parser.add_argument('uid', nargs='?', type=int, help='User ID')
    parser.add_argument('subject', nargs='?', help='Subject of the message')
    parser.add_argument('num', nargs='?', type=int,
                        help='Number of the message')
    args = parser.parse_args()
    user_data = args.userdata

    # open connection
    reader, writer = await asyncio.open_connection('127.0.0.1', conn_port)

    # initialize client
    addr = writer.get_extra_info('peername')
    client = Client(user_data, addr)

    # send public DH key to server
    writer.write(client.dh_key())
    print("> Sent public DH key.")

    # receive public key, cert and signature from server
    server_info = await reader.read(max_msg_size)
    print("> Received public key, cert and signature.")

    # process server info
    client_info = client.process_server_info(server_info)

    # send public key, cert and signature to server
    writer.write(client_info)
    print("> Sent public key, cert and signature.")

    match args.command:
        case 'send':
            # get message to send from user
            msg_send = input("> Input message to send: ")

            # send message to server
            writer.write(aes_ctr.cipher(
                f"send|{args.uid}|{args.subject}|{msg_send}".encode(), client.shared_key))

            # receive response from server
            output = await reader.read(max_msg_size)

            # print response
            print(aes_ctr.decipher(output, client.shared_key).decode())

        case 'askqueue':
            # send message to server
            writer.write(aes_ctr.cipher(
                f"askqueue|{args.userdata}".encode(), client.shared_key))
            # receive response from server
            output = await reader.read(max_msg_size)
            # print response
            print(aes_ctr.decipher(output, client.shared_key).decode())

        case 'getmsg':
            # send message to server
            writer.write(aes_ctr.cipher(
                f"getmsg|{args.uid}".encode(), client.shared_key))
            # receive response from server
            output = await reader.read(max_msg_size)
            # print response
            print(aes_ctr.decipher(output, client.shared_key).decode())

        case "help":
            help()

        case "-user":
            client.userdata_file = args.userdata

        case _:
            print("Invalid command. Use 'help' to see the available commands.")

    print('Closing connection...')
    writer.close()


# MAIN


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tcp_echo_client())


main()
