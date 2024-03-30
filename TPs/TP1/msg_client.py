# Código baseado em https://docs.python.org/3.6/library/asyncio-stream.html#tcp-echo-client-using-streams
import asyncio
import argparse
import socket
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import padding
import validate_cert
import os

conn_port = 8443
max_msg_size = 9999
p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
g = 2
ca_cert = x509.load_pem_x509_certificate(open("MSG_CLI1.crt", "rb").read())
end = 0


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
        self.aesgcm = None
        file = f"{user_data}.p12"
        print(file)
        with open(file, "rb") as p12_file:
            (self.rsaprivate_key, self.cert, _) = serialization.pkcs12.load_key_and_certificates(
                p12_file.read(),
                password=None,
            )
        print(self.rsaprivate_key)
        print(self.cert)
        # pkcs12 load_key_and_certificates , ficheiro e a passe None
        # passe server 1234

    def process(self, msg=b""):
        """ Processa uma mensagem (`bytestring`) enviada pelo SERVIDOR.
            Retorna a mensagem a transmitir como resposta (`None` para
            finalizar ligação) """
        self.msg_cnt += 1
        if not msg and self.msg_cnt == 1:
            publicKey = self.dhprivate_key.public_key()
            pem = publicKey.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            print("Sending public DH key.")
            return pem
        split = unpair(msg)[0].splitlines()
        if len(split) > 0 and unpair(msg)[0].splitlines()[0] == b'-----BEGIN PUBLIC KEY-----':
            print("Entrei")
            print("Received public key, cert and signature.")
            print(unpair(msg)[0])
            server_dh_pub = serialization.load_pem_public_key(unpair(msg)[0])
            print(unpair(unpair(msg)[1]))
            print(server_dh_pub)
            signature, cert_name = unpair(unpair(msg)[1])
            cert_name = cert_name.decode()
            # Verifica o certificado
            cert = x509.load_pem_x509_certificate(cert_name.encode())

            # print(validate_cert.valida_cert(cert_name, "Server"))
            # print(cert_name)
            if not validate_cert.valida_cert(cert, "Server"):
                print("Certicate is not valid")
                return None
            print("Certificate is valid")

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

            if not valida_rsa_signature(server_rsa_public_key, signature, dh_pair):
                print("Signature is not valid")
                return None
            print("Signature is valid")

            # Gera a chave partilhada
            shared_key = self.dhprivate_key.exchange(server_dh_pub)
            self.shared_key = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b'handshake data',
            ).derive(shared_key)

            # Inicializa o AESGCM
            self.aesgcm = AESGCM(self.shared_key)
            print("AESGCM initialized.")

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
            print("Sending public key, cert and signature.")
            return pair2

        if not (len(split) > 0 and msg.splitlines()[0] == b'-----BEGIN PUBLIC KEY-----') and msg:
            nonce = msg[:12]
            ciphertext = msg[12:]
            msg = self.aesgcm.decrypt(nonce, ciphertext, None)

        print('Received (%d): %r' % (self.msg_cnt, msg.decode()))
        print('Input message to send (empty to finish)')
        new_msg = input().encode()

        nonce = os.urandom(12)
        ciphertext = nonce + self.aesgcm.encrypt(nonce, new_msg, None)

        return ciphertext if len(ciphertext) > 0 else None

    def send_msg(self, args):
        """
        Send a message to the server.
        """
        # msg = self.process(args)
        msg = f'send {args.uid} {args.subject}\n'
        # self.writer.write(f'send {uid} {subject} {message}\n'.encode())
        # await self.writer.drain()
        # return message.encode()
        return msg


def handle_commands(client, args):
    print(args)
    if args.command == 'send':
        return f"send {args.uid} {args.subject}\n"
    elif args.command == "-user":
        print(args)
        client.userdata_file = args.userdata
    elif args.command == 'askqueue':
        # client.ask_queue()
        pass
    elif args.command == 'getmsg':
        # client.get_msg(args.uid)
        pass
    elif args.command == 'help':
        help()
    else:
        print("Not valid")


@staticmethod
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
#
#
# Funcionalidade Cliente/Servidor
#
# obs: não deverá ser necessário alterar o que se segue
#


async def tcp_echo_client():
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
    reader, writer = await asyncio.open_connection('127.0.0.1', conn_port)
    addr = writer.get_extra_info('peername')
    client = Client(user_data, addr)
    text = handle_commands(client, args)
    print(text)
    msg = client.process()
    writer.write(msg)
    msg = await reader.read(max_msg_size)
    if msg:
        msg = client.process(msg)
        print(msg)
    print("Aqui")
    match args.command:
        case 'send':
            if text != None:
                print("Entrei")
                writer.write(text.encode())
                print("A")
                while msg:
                    # msg = await reader.read(max_msg_size)
                    if msg:
                        msg = client.process(msg)
                    else:
                        break
        case 'askqueue':
            linha = f"askqueue\n{args.userdata}\n"
            writer.write(bytes(linha, 'utf-8'))
            output = await reader.read(max_msg_size)
            print(output.decode())
        case 'getmsg':
            linha = f"getmsg\n{args.uid}\n"
            writer.write(bytes(linha, 'utf-8'))
            output = await reader.read(max_msg_size)
            print(output.decode())
    writer.write(b'\n')
    print('Socket closed!')
    writer.close()


def run_client():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tcp_echo_client())


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


def valida_rsa_signature(rsa_public_key, signature, data):
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


def load_cert(cert_name):
    print(cert_name)
    with open(cert_name, "rb") as cert_file:
        return cert_file.read()


run_client()
