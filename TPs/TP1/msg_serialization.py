from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization


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


class SerializeSend:
    def bundle_message(self, message: str, client) -> bytes:
        # sign message
        signature = client.rsaprivate_key.sign(
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # join signature with certificate
        pair = mkpair(signature, client.cert.public_bytes(
            encoding=serialization.Encoding.PEM))

        # join signature and certificate to message
        return mkpair(pair, message.encode())

    def serialize(self, sender: str, receiver: str, subject: str, message: str, client) -> bytes:
        # add send command info
        data = f"send|{sender}|{receiver}|{subject}|".encode()

        # bundle message with necessary info
        data += self.bundle_message(message, client)

        return data

    def deserialize(self, data: bytes) -> list:
        b_array = bytearray(data)

        sender = ""
        c: str = b_array[0:1].decode()
        while c != "|":
            sender += c
            b_array = b_array[1:]
            c = b_array[0:1].decode()

        # skip "|"
        b_array = b_array[1:]

        receiver = ""
        c: str = b_array[0:1].decode()
        while c != "|":
            receiver += c
            b_array = b_array[1:]
            c = b_array[0:1].decode()

        # skip "|"
        b_array = b_array[1:]

        subject = ""
        c: str = b_array[0:1].decode()
        while c != "|":
            subject += c
            b_array = b_array[1:]
            c = b_array[0:1].decode()

        # skip "|"
        b_array = b_array[1:]

        return [sender, receiver, subject, bytes(b_array)]


class SerializeGetMsg:
    def unbundle_message(self, data: bytes):
        # get pair and message
        pair, message = unpair(data)

        # get signature and certificate
        signature, cert = unpair(pair)

        return signature, cert, message

    def serialize(self, num: str, uid: str) -> bytes:
        return f"getmsg|{num}|{uid}".encode()

    def deserialize(self, data: bytes) -> list:
        return data.decode().split("|")


class SerializeAskQueue:
    def serialize(self, uid: str) -> bytes:
        return f"askqueue|{uid}".encode()

    def deserialize(self, data: bytes) -> list:
        return data.decode().split("|")


class Serializer:
    def __init__(self):
        self.send = SerializeSend()
        self.getmsg = SerializeGetMsg()
        self.askqueue = SerializeAskQueue()

    def deserialize(self, data: bytes) -> list:
        b_array = bytearray(data)

        command = ""
        c: str = b_array[0:1].decode()
        while c.isalpha() and c != "|":
            command += c
            b_array = b_array[1:]
            c = b_array[0:1].decode()

        # skip "|"
        b_array = b_array[1:]

        match command:
            case "send":
                return [command] + self.send.deserialize(b_array)

            case "getmsg":
                return [command] + self.getmsg.deserialize(b_array)

            case "askqueue":
                return [command] + self.askqueue.deserialize(b_array)

            case _:
                raise Exception("Unknown command.")
