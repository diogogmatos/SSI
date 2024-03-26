import argparse
import sys
import asyncio
import util

conn_port = 8443
max_msg_size = 9999

class Client:
    """ Classe que implementa a funcionalidade de um CLIENTE. """

    def __init__(self, writer, reader, sckt=None, userdata_file='MSG_CLI1.p12'):
        """ Construtor da classe. """
        self.writer = writer
        self.reader = reader
        self.sckt = sckt
        self.msg_cnt = 0
        self.userdata_file = userdata_file

    def process(self, msg=b""):
        """ Processa uma mensagem (`bytestring`) enviada pelo SERVIDOR.
            Retorna a mensagem a transmitir como resposta (`None` para
            finalizar ligação) """
        if len(msg) != 0:
            self.msg_cnt += 1
            nonce = msg[:12]
            salt = msg[12:28]
            content = msg[28:]
            #msg = util.decrypt_AESGCM(nonce, salt, content)
            print('Received (%d): %r' % (self.msg_cnt, msg))
        print('Input message to send (empty to finish)')
        new_msg = input().encode()
        if len(new_msg) > 0:
            new_msg = util.encrypt_AESGCM(new_msg)
        return new_msg if len(new_msg) > 0 else None

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

    async def send_msg(self, uid, subject):
        """
        Send a message to the server.
        """
        msg = self.process()
        while msg:
            print("ABC")
            print(uid)
            print(msg)
            uid_bytes = uid.to_bytes(4, 'big')
            self.writer.write(b'send\n')
            self.writer.write(uid_bytes)
            self.writer.write(b'\n')
            self.writer.write(subject.encode())
            self.writer.write(b'\n')
            self.writer.write(msg)
            print(f"Mensagem enviada: {msg}")
            print(f"UID: {uid_bytes}")
            #msg = await self.reader.read(max_msg_size)
            print(msg)
            if msg:
                print("ABC2")
                msg = self.process(msg)
                print(msg)
            else:
                break
        self.writer.write(b'\n')
        print('Closing connection...')
        self.writer.close()
        # self.writer.write(f'send {uid} {subject} {message}\n'.encode())
        # await self.writer.drain()
        #return message.encode()
        print("Message sent successfully!")

    async def ask_queue(self):
        """
        Ask the server for the non read messages in the queue for the user.
        """
        self.writer.write(b'askqueue\n')
        

    async def get_msg(self, num):
        """
        Get the message with the number <NUM> from the queue.
        """
        print(num)
        num_bytes = num.to_bytes(4, 'big')
        self.writer.write(b'getmsg\n')
        self.writer.write(num_bytes)
        self.writer.write(b'\n')
        valor = await self.reader.read(max_msg_size)
        print(valor)

async def handle_commands(client, args):
    print(args)
    if args.command == 'send':
        print(args)
        await client.send_msg(args.uid, args.subject)
    elif args.command == "-user":
        print(args)
        client.userdata_file = args.userdata
    elif args.command == 'askqueue':
        await client.ask_queue()
    elif args.command == 'getmsg':
        await client.get_msg(args.uid)
    elif args.command == 'help':
        client.help()

async def tcp_echo_client():
    parser = argparse.ArgumentParser(description='Client for TCP Echo Server')
    parser.add_argument('-user', dest='userdata', default='MSG_CLI1.p12', help='Specify user data file (default: userdata.p12)')
    parser.add_argument('command', choices=['send', 'askqueue', 'getmsg', 'help'], help='Command to execute')
    parser.add_argument('uid', nargs='?', type=int, help='User ID')
    parser.add_argument('subject', nargs='?', help='Subject of the message')
    parser.add_argument('num', nargs='?', type=int, help='Number of the message')
    args = parser.parse_args()
    
    reader, writer = await asyncio.open_connection('127.0.0.1', conn_port)
    addr = writer.get_extra_info('peername')
    client = Client(writer, reader, addr, args.userdata)
    print(args)
    await handle_commands(client, args)
    
    writer.write(b'\n')
    print('Socket closed!')
    writer.close()

def run_client():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tcp_echo_client())

if __name__ == "__main__":
    run_client()
