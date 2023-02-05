
from authenticator import Authenticator

BUFFER_SIZE = 1024

class ServerConn:

    def __init__(self, conn, addr) -> None:
        self.conn = conn
        self.addr = addr
        self.authenticator = Authenticator()
        self.connOpen = True
        self.currentDir = 'SFS-Shell:~'

    # This is the main loop of our serverconnection threads
    def run(self) -> None:

        ######### authenticate with user here

        print(f"New connection to {self.addr}")
        while self.connOpen: ### main loop
            try:
                # show client their current position in the SFS shell
                self.__send(self.currentDir)

                message = self.__receive()
                if message:
                    print(f"recieved message from {self.addr}: {message}")
                else: # client no longer responding
                    self.__close()
            except Exception:
                self.__close()

    # This method listens for data sent by the client
    def __receive(self) -> str:
        data = self.conn.recv(BUFFER_SIZE)
        if not data:
            return
        message = data.decode('utf-8')
        return message
    
    # This method listens for data sent by the client in chunks, ending at a '\r\n' sequence
    def __receiveChunks(self) -> str:
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
    
    def __send(self, data) -> None:
        self.conn.send(data.encode('utf-8'))

    def __sendFile(self, filename) -> bool:
        # todo
        pass

    def __receiveFile(self, filename) -> None:
        # todo
        pass
    
    def __close(self) -> None:
        self.conn.close()
        self.connOpen = False
