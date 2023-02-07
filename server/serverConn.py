
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
                self.send(self.currentDir)

                message = self.receive()
                if message:
                    print(f"recieved message from {self.addr}: {message}")
                    pass
                else: # client no longer responding
                    self.close()
            except Exception:
                self.close()

    # This method listens for data sent by the client
    def receive(self) -> str:
        data = self.conn.recv(BUFFER_SIZE)
        if not data:
            return
        message = data.decode('utf-8')
        return message
    
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
            # print(f"received chunk: {chunk}")
            chunks.append(chunk)
        message = (b''.join(chunks)).decode('utf-8')
        return message.rstrip('\r\n')
    
    def send(self, data) -> None:
        self.conn.send(data.encode('utf-8'))

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
            print(f'Connection to {self.addr} closed.')
