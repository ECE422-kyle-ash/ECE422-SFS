
import logging
from cryptography.fernet import Fernet

from authenticator import Authenticator
from serverState import State
from serverState import MainState
from serverState import AuthenticateState
# from serverState import LoginState
from serverState import ExchangeKeyState

BUFFER_SIZE = 1024

class ServerConn:

    def __init__(self, conn, addr) -> None:
        self.conn = conn
        self.addr = addr
        self.authenticator = Authenticator()
        self.connOpen = True
        self.currentDir = 'SFS-Shell:~'
        self.state = State()
        self.fernet = None

    # This is the main loop of our serverconnection threads
    def run(self) -> None:

        logging.info(f"New connection to {self.addr}")

        self.state = ExchangeKeyState()

        
        while self.connOpen: ### main loop
            self.state.run(server=self)
    
    # This method listens for data sent by the client in chunks, ending at a '\r\n' sequence
    def receiveChunks(self) -> str:
        chunks = []
        while True:
            chunk = self.conn.recv(BUFFER_SIZE)
            if not chunk: # client has disconnected
                return
            elif chunk.endswith(b'\r\n'):
                chunks.append(chunk)
                break
            # logging.debug(f"received chunk: {chunk}")
            chunks.append(chunk)
        message = (b''.join(chunks)).decode('utf-8')
        return message.rstrip('\r\n')
    
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

    def receiveFile(self, filename) -> None:
        # todo
        pass
    
    def close(self) -> None:
        if self.connOpen == True:
            self.conn.close()
            self.connOpen = False
            logging.info(f'Connection to {self.addr} closed.')
