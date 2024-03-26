# Código baseado em https://docs.python.org/3.6/library/asyncio-stream.html#tcp-echo-client-using-streams
import asyncio
from datetime import datetime
import json

conn_cnt = 0
conn_port = 8443
max_msg_size = 9999


class ServerWorker(object):
    """ Classe que implementa a funcionalidade do SERVIDOR. """

    def __init__(self, cnt, addr=None):
        """ Construtor da classe. """
        self.id = cnt
        self.addr = addr
        self.msg_cnt = 0

    def process(self, msg, srvwrk):
        """ Processa uma mensagem (`bytestring`) enviada pelo CLIENTE.
            Retorna a mensagem a transmitir como resposta (`None` para
            finalizar ligação) """
        print(msg)
        msg = msg.split(b'\n')
        print(msg)
        self.msg_cnt += 1
        return self.handle(msg, srvwrk)
        # print(uid) # UID
        # print(msg[1]) # SUBJECT
        # print(msg[2]) # MSG
        # Faz o decrypt correto da mensagem, abaixo
        #nonce = msg[:12]
        #salt = msg[12:28]
        #content = msg[28:]
        #msg = util.decrypt_AESGCM(nonce, salt, content)
        #txt = msg.decode()
        #print('%d : %r' % (self.id, msg))
        #new_msg = txt.upper().encode()

        #return util.encrypt_AESGCM(new_msg) if len(new_msg) > 0 else None

    def database_write(self, uid, subject, msg, srvwrk):
        """
        Write the message to the database.
        """
        try:
            with open('database.json', 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        uid = f"{str(srvwrk.id)}:{str(uid)}:{current_time}:{subject.decode()}"
        print(uid)
        if uid in data:
            data[uid].append((msg.hex(), False))
            # Para converter de volta
            # print(bytes.fromhex(msg_hex))
        else:
            data[uid] = [(msg.hex(), False)]
        with open('database.json', 'w') as f:
            json.dump(data, f)
    
    def database_read(self, num):
        """
        Read the messages from the database.
        """
        try:
            with open('database.json', 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        

        for k, v in data.items():
            print(k)
            if k.startswith(str(num)):
                return v
        return None
    
    def handle(self, msg, srvwrk):
        """
        Handle the message.
        """
        match msg[0]:
            case b'send':
                uid = int.from_bytes(msg[1], 'big')
                self.database_write(uid, msg[2], msg[3], srvwrk)
            case b'askqueue':
                print("Ask queue")
            case b'getmsg':
                print("Get message")
                print(msg[1])
                num = int.from_bytes(msg[1], 'big')
                msg = self.database_read(num)
                return msg
            case _:
                print("Invalid command")

#
#
# Funcionalidade Cliente/Servidor
#
# obs: não deverá ser necessário alterar o que se segue
#


async def handle_echo(reader, writer):
    global conn_cnt
    conn_cnt += 1
    addr = writer.get_extra_info('peername')
    srvwrk = ServerWorker(conn_cnt, addr)
    data = await reader.read(max_msg_size)
    while True:
        if not data: continue
        data = srvwrk.process(data, srvwrk)
        print(f"ABC: {data}")
        if not data: break
        hex_string = data[0][0]
        print(hex_string)
        byte_data = bytes.fromhex(hex_string)
        writer.write(byte_data)
        await writer.drain()
        print("aqui")
    return data


def run_server():
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
    print('\nFINISHED!')


run_server()
