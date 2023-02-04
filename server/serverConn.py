
import socket

from authenticator import Authenticator

BUFFER_SIZE = 1024

class ServerConn:

    def __init__(self, conn, addr) -> None:
        self.conn = conn
        self.addr = addr
        self.authenticator = Authenticator()
        self.connOpen = True

    def run(self) -> None:
        # with self.conn: # ensures there is a connection
        print(f"New connection to {self.addr}")
        while self.connOpen:
            try:
                message = self.__receive()
                if message:
                    print(f"recieved message from {self.addr}: {message}")
                else: # client no longer responding
                    self.__close()
            except Exception:
                self.__close()

    def __receive(self) -> str:
        chunks = []
        while True:
            chunk = self.conn.recv(BUFFER_SIZE)
            if not chunk: # client has disconnected
                return
            elif chunk.endswith(b'\r\n'):
                chunks.append(chunk)
                break
            # print(f"received chunk: {chunk}")
            chunks.append(chunk)
        message = (b''.join(chunks)).decode('utf-8')
        return message.rstrip('\r\n')
    
    def __send(self) -> bool:
        # todo
        pass

    def __sendFile(self, filename) -> bool:
        # todo
        pass

    def __receiveFile(self, filename) -> None:
        # todo
        pass
    
    def __close(self) -> None:
        self.conn.shutdown(socket.SHUT_RDWR)
        self.conn.close()
        self.connOpen = False
