# Código baseado em https://docs.python.org/3.6/library/asyncio-stream.html#tcp-echo-client-using-streams
import asyncio
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509
import validate_cert
import bson
from datetime import datetime
import aes_gcm
import os


# CONSTANTS


conn_cnt = 0
conn_port = 8443
max_msg_size = 9999
p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
g = 2
ca_cert = x509.load_pem_x509_certificate(
    open("projCA/certs/MSG_SERVER.crt", "rb").read())


# def load_cert(cert_name):
#     with open(cert_name, "rb") as cert_file:
#         return cert_file.read()


# SERVER


# chave publica que esta no certificado, assinatura e dados que é suposto estarem assinados
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


class ServerWorker(object):
    """ Classe que implementa a funcionalidade do SERVIDOR. """

    def __init__(self, cnt, addr=None):
        """ Construtor da classe. """
        self.id = cnt
        self.addr = addr
        self.msg_cnt = 0
        self.dhprivate_key = dh.DHParameterNumbers(
            p, g).parameters().generate_private_key()
        # generate a 256 bits key from the private key to cipher database data with AES_CTR
        self.database_key = self.dhprivate_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )[:32]
        self.rsaprivate_key = None
        self.shared_key = None

        with open("projCA/certs/MSG_SERVER.p12", "rb") as p12_file:
            (self.rsaprivate_key, self.cert, _) = serialization.pkcs12.load_key_and_certificates(
                p12_file.read(),
                password=None,
            )

    def askqueue(self, uid: str):
        messages = []

        # extract message texts
        with open("database.bson", "rb") as file:
            # decipher file data
            data = aes_gcm.decipher(file.read(), self.database_key)
            # decod data as BSON
            bson_data = bson.BSON(data).decode()
            for key, value in bson_data.items():
                msg_info = key.split("|")
                sender = msg_info[1]
                if sender == uid and not value[1]:
                    messages.append(key.replace("|", ":"))

        # check if there are no messages
        if not messages:
            return "No unread messages found.".encode()
        
        # sort messages based on time
        messages.sort(key=lambda x: x[0])

        return "\n".join(messages).encode()

    def get_msg(self, num):
        r: bytes = b''
        bson_data = {}

        # open file and get message
        with open("database.bson", "rb") as file:
            # decipher file data
            data = aes_gcm.decipher(file.read(), self.database_key)
            # decode data as BSON
            bson_data = bson.BSON(data).decode()
            
            # find requested message
            for key, value in bson_data.items():
                msg_info = key.split("|")
                msg_num = msg_info[0]                
                if msg_num == num:
                    if not value[1]:
                        value[1] = True
                        print(f"> Message {num} marked as read.")
                    r = f"{msg_info[3]}\n\n{value[0]}".encode()
        
        # update file with message marked as read
        with open("database.bson", "wb") as file:
            file.write(aes_gcm.cipher(bson.BSON.encode(bson_data), self.database_key))

        return r

    def store_msg(self, sender, subject, message):
        bson_data = {}

        # create database file if it doesn't exist
        if not os.path.exists("database.bson"):
            with open('database.bson', 'xb') as file:
                # store ciphered empty BSON data
                file.write(aes_gcm.cipher(bson.BSON.encode({}), self.database_key))
        
        # open existing database file
        else:            
            with open('database.bson', 'rb') as file:
                # decipher file data
                data = aes_gcm.decipher(file.read(), self.database_key)
                # decode data as BSON
                bson_data = bson.BSON(data).decode()

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # generate a new message number
        new_message_num = str(len(bson_data) + 1)

        # create the new key in the format "<NUM>:<SENDER>:<TIME>:<SUBJECT>"
        new_key = f"{new_message_num}|{sender}|{current_time}|{subject}"

        # add the new message to the BSON data
        bson_data[new_key] = message, False

        # write the updated BSON data back to the file
        with open('database.bson', 'wb') as file:
            # store ciphered data
            file.write(aes_gcm.cipher(bson.BSON.encode(bson_data), self.database_key))

        print(f"> New message to {sender} stored successfully.")

    def handle_commands(self, msg):
        try:
            msg = msg.decode()
            msg = msg.split("|")
        except:
            return None

        match msg[0]:
            case "askqueue":
                print(msg)
                return self.askqueue(msg[1])

            case "getmsg":
                return self.get_msg(msg[1])

            case "send":
                self.store_msg(msg[1], msg[2], msg[3])
                return "Message sent successfully.".encode()

            case _:
                return None

    def process(self, msg):
        """ Processa uma mensagem (`bytestring`) enviada pelo CLIENTE.
            Retorna a mensagem a transmitir como resposta (`None` para
            finalizar ligação) """

        # increase msg count
        self.msg_cnt += 1

        # try to process a user command
        r = self.handle_commands(msg)
        if r != None:
            return r

        # if msg is not a command (initial messages):

        # process DH key
        if msg.splitlines()[0] == b'-----BEGIN PUBLIC KEY-----':
            print("> Received public DH key.")
            client_dh_pub = serialization.load_pem_public_key(msg)
            # Cria o par de chaves públicas
            dh_pair = mkpair(
                self.dhprivate_key.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ),
                client_dh_pub.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )
            # Gera a assinatura do par de chaves
            signature = self.rsaprivate_key.sign(
                dh_pair,  # Chave pública do servidor
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
            print("> Sending public key, cert and signature.")
            return pair2

        # process public key, cert and signature
        if unpair(msg)[0].splitlines()[0] == b'-----BEGIN PUBLIC KEY-----':
            print("> Received public key, cert and signature.")
            server_dh_pub = serialization.load_pem_public_key(unpair(msg)[0])
            signature, cert_name = unpair(unpair(msg)[1])
            cert_name = cert_name.decode()

            # Verifica o certificado
            cert = x509.load_pem_x509_certificate(cert_name.encode())

            if not validate_cert.valida_cert(cert, "User 1 (SSI MSG Relay Client 1)"):
                print("✗ Certicate is not valid")
                return -1
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
                return -1
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


# MAIN FUNCTIONALITY


async def handle_echo(reader, writer):
    global conn_cnt

    # increase connection count
    conn_cnt += 1
    print("✓ New connection established:", conn_cnt)

    # initialize server worker
    addr = writer.get_extra_info('peername')
    srvwrk = ServerWorker(conn_cnt, addr)

    # read first message
    data = await reader.read(max_msg_size)

    # read continuously
    # try:
    while data and data != -1 and data[:1] != b'\n':
        # decipher received data
        if srvwrk.shared_key != None:
            data = aes_gcm.decipher(data, srvwrk.shared_key)

        # process data and get a response
        res = srvwrk.process(data)

        # send response
        if res != None:
            # cipher response
            if srvwrk.shared_key != None:
                res = aes_gcm.cipher(res, srvwrk.shared_key)

            writer.write(res)
            await writer.drain()
            print("> Sent response.")

        # wait for next message
        print("> Waiting for next message...")
        data = await reader.read(max_msg_size)
    # except Exception as e:
    #     print("ERROR:", e)

    print(f"✗ Connection closed: {srvwrk.id}")
    writer.close()


# MAIN


def main():
    loop = asyncio.new_event_loop()
    coro = asyncio.start_server(handle_echo, '127.0.0.1', conn_port)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    print('  (type ^C to finish)\n')
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
    print('\b\bClosing server...')


main()
