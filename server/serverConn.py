
import logging
from cryptography.fernet import Fernet

from authenticator import Authenticator
import serverState

BUFFER_SIZE = 2048

class ServerConn:

    def __init__(self, conn, addr) -> None:
        self.conn = conn
        self.addr = addr
        self.authenticator = Authenticator()
        self.connOpen = True
        self.state = serverState.State()
        self.fernet = None

    # This is the main loop of our serverconnection threads
    def run(self) -> None:

        logging.info(f"New connection to {self.addr}")

        self.state = serverState.ExchangeKeyState()

        while self.connOpen: ### main loop
            self.state.run(server=self)
    
    # This method listens for data sent by the client
    def receive(self) -> str:
        data = self.conn.recv(BUFFER_SIZE)
        if not data:
            return
        message = self.fernet.decrypt(data).decode('utf-8')
        return message
    
    def send(self, data) -> None:
        crypto = self.fernet.encrypt(data.encode('utf-8'))
        self.conn.send(crypto)

    def sendFile(self, filename) -> bool:
        # todo
        pass

    # This method listens for data sent by the client in chunks, ending at a '\r\n' sequence
    def receiveChunks(self) -> str:
        chunks = []
        while True:
            try:
                chunk = self.conn.recv(BUFFER_SIZE)
            except Exception as e:
                logging.error(e)
            if not chunk: # client has disconnected
                logging.error(f'Client: {self.addr} has disconnected during receiveChunks')
                return
            chunk = self.fernet.decrypt(chunk).decode('utf-8')
            chunks.append(chunk)
            if chunk.endswith('\x04'):
                # self.send('EOFOK')
                message = (''.join(chunks))
                return message.rstrip('\x04')
            # self.send('OK')

    # def receiveFile(self, filename) -> bool:
    #     content = self.receiveChunks()
    #     if content: # save file
    #         logging.info(f'Received contents of: {filename} from: {self.addr}')
    #         return self.saveFile(filename, content)
    #     return False
    
    # def saveFile(self, filename, content) -> bool: # todo ash
    #     filepath = '../test/res_'+filename
    #     logging.info(f'Saving content to {filepath}')
    #     with open(filepath, 'w') as f:
    #         try:
    #             f.write(content)
    #             f.close()
    #             return True
    #         except:
    #             return False
    
    def close(self) -> None:
        if self.connOpen == True:
            self.conn.close()
            self.connOpen = False
            logging.info(f'Connection to {self.addr} closed.')
