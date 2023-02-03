
class ServerConn:

    def __init__(self, conn, addr) -> None:
        self.conn = conn
        self.addr = addr

    def run(self) -> None:
        with self.conn as conn: # ensures there is a connection
            print(f"New connection to {self.addr}")
            message = self.__receive(conn)
            print(f"recieved message from {self.addr}: {message}")

    def __receive(self, conn) -> str:
        chunks = []
        bytes_recd = 0
        while True:
            chunk = conn.recv(1024)
            if not chunk:
                break
            # print(f"received chunk: {chunk}")
            chunks.append(chunk)
        message = (b''.join(chunks)).decode('utf-8')
        return message