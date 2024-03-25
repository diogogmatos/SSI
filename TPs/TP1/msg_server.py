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

    def process(self, msg):
        """ Processa uma mensagem (`bytestring`) enviada pelo CLIENTE.
            Retorna a mensagem a transmitir como resposta (`None` para
            finalizar ligação) """
        msg = msg.split(b'\n')
        self.msg_cnt += 1
        uid = int.from_bytes(msg[0], 'big')
        print(uid)
        print(msg[1])
        print(msg[2])
        self.database_write(uid, msg[1], msg[2])
        # Faz o decrypt correto da mensagem, abaixo
        #nonce = msg[:12]
        #salt = msg[12:28]
        #content = msg[28:]
        #msg = util.decrypt_AESGCM(nonce, salt, content)
        #txt = msg.decode()
        #print('%d : %r' % (self.id, msg))
        #new_msg = txt.upper().encode()

        #return util.encrypt_AESGCM(new_msg) if len(new_msg) > 0 else None

    def database_write(self, uid, subject, msg):
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
        print(current_time)
        # Missing, number of message
        uid = str(uid) + ":" + current_time + ":" + subject.decode()
        if uid in data:
            data[uid].append(msg.hex())
            # Para converter de volta
            # print(bytes.fromhex(msg_hex))
        else:
            data[uid] = [msg.hex()]
        with open('database.json', 'w') as f:
            json.dump(data, f)

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
        data = srvwrk.process(data)
        if not data: break
        writer.write(data)
        await writer.drain()
        data = await reader.read(max_msg_size)
    print("[%d]" % srvwrk.id)
    writer.close()


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
