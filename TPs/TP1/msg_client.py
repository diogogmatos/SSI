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
import sys
import aes_gcm
import msg_serialization

# CONSTANTS

conn_port = 8443
max_msg_size = 9999
p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
g = 2
ca_cert = x509.load_pem_x509_certificate(
    open("projCA/certs/MSG_CLI1.crt", "rb").read())
end = 0

serializer = msg_serialization.Serializer()


# CLIENT


def validate_signature(signature, cert, data):
    try:
        cert.public_key().verify(
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


class Client:
    """ Classe que implementa a funcionalidade de um CLIENTE. """

    def __init__(self, userdata="projCA/certs/MSG_CLI1", sckt=None):
        """ Construtor da classe. """
        self.sckt = sckt
        self.msg_cnt = 0
        self.dhprivate_key = dh.DHParameterNumbers(
            p, g).parameters().generate_private_key()
        self.rsaprivate_key = None
        self.cert = None
        self.shared_key = None
        self.user_data_file = f"{userdata}.p12"
        #
        with open(self.user_data_file, "rb") as p12_file:
            self.rsaprivate_key, self.cert, _ = serialization.pkcs12.load_key_and_certificates(
                p12_file.read(),
                password=None,
            )

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
            msg_serialization.unpair(server_info)[0])
        signature, cert_name = msg_serialization.unpair(
            msg_serialization.unpair(server_info)[1])
        cert_name = cert_name.decode()

        # Verifica o certificado

        cert = x509.load_pem_x509_certificate(cert_name.encode())

        if not validate_cert.valida_cert(cert, "Server"):
            print("✗ Certicate is not valid")
            return None
        print("✓ Certificate is valid")

        # Verifica a assinatura

        dh_pair = msg_serialization.mkpair(
            server_dh_pub.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ),
            self.dhprivate_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo)
        )

        if not validate_signature(signature, cert, dh_pair):
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

        # cert + assinatura com mensagem

        signature = self.rsaprivate_key.sign(
            msg_serialization.mkpair(
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

        sig_cert = msg_serialization.mkpair(signature, self.cert.public_bytes(
            encoding=serialization.Encoding.PEM))
        pubkey_sig_cert = msg_serialization.mkpair(
            self.dhprivate_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo),
            sig_cert
        )

        return pubkey_sig_cert


# MAIN FUNCTIONALITY


async def tcp_echo_client():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-user', dest='userdata', default='projCA/certs/MSG_CLI1',
                        help='specify user data file path')
    parser.add_argument('command', choices=[
                        'send', 'askqueue', 'getmsg', 'help'], help='command to execute')
    parser.add_argument('uid_num', nargs='?', help='user id || message number')
    parser.add_argument('subject', nargs='?', help='subject of the message')

    try:
        args = parser.parse_args()
    except:
        sys.stderr.write("MSG RELAY SERVICE: command error!\n")
        return

    if args.command == "help":
        parser.print_help()
        return

    # open connection
    reader, writer = await asyncio.open_connection('127.0.0.1', conn_port)

    # initialize client
    addr = writer.get_extra_info('peername')
    client = Client(args.userdata, addr)

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

    try:
        match args.command:
            case 'send':
                # get message to send from user
                msg_send = input("> Input message to send: ")

                # check message length
                if sys.getsizeof(msg_send) > 1000:
                    raise ValueError(
                        "The message is too long. Maximum size is 1000 bytes.")

                # send message to server
                writer.write(aes_gcm.cipher(serializer.send.serialize(
                    args.userdata, args.uid_num, args.subject, msg_send, client), client.shared_key))

                # receive response from server
                output = await reader.read(max_msg_size)

                # print response
                print(aes_gcm.decipher(output, client.shared_key).decode())

            case 'askqueue':
                # send message to server
                writer.write(aes_gcm.cipher(serializer.askqueue.serialize(
                    args.userdata), client.shared_key))

                # receive response from server
                output = await reader.read(max_msg_size)

                # print response
                print(
                    f"> Unread messages:\n\n{aes_gcm.decipher(output, client.shared_key).decode()}\n")

            case 'getmsg':
                # send message to server
                writer.write(aes_gcm.cipher(
                    serializer.getmsg.serialize(args.uid_num, args.userdata), client.shared_key))

                # receive response from server
                output = await reader.read(max_msg_size)
                deciphered_output = aes_gcm.decipher(output, client.shared_key)

                # get data for message verification and message
                signature, certificate, message = serializer.getmsg.unbundle_message(
                    deciphered_output)

                err = False
                response = ""

                # perform validations

                # check if message was found
                if message == b"":
                    err = True
                    response = "MSG RELAY SERVICE: unknown message!\n"

                # validate certificate and signature
                elif not validate_cert.valida_cert(x509.load_pem_x509_certificate(certificate), "") or not validate_signature(signature, x509.load_pem_x509_certificate(certificate), message):
                    err = True
                    response = "MSG RELAY SERVICE: verification error!\n"

                else:
                    print("✓ Message verified")
                    response = f"> Here's message {args.uid_num}:\n\n{message.decode()}\n"

                # print response
                if err:
                    sys.stderr.write(response)
                else:
                    print(response)

            case "-user":
                client.user_data_file = args.userdata

            case _:
                sys.stderr.write("MSG RELAY SERVICE: command error!\n")
    except Exception as e:
        print("ERROR:", e, file=sys.stderr)

    print('Closing connection...')
    writer.close()


# MAIN


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tcp_echo_client())


main()
