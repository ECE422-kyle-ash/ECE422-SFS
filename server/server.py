import socket
from multiprocessing import Process

class Server:
    # https://docs.python.org/3/howto/sockets.html

    def __init__(self, port=8080) -> None:
        self.port = port

    def run(self) -> None:
        with socket.socket() as serversocket:
            serversocket.bind(('localhost', self.port))
            serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            serversocket.listen(2) # allow backlog of 2

            while True:
                conn, addr = serversocket.accept()
                thread = Process(target=self.__handle_connection, args=(conn, addr,), daemon=True)
                thread.start()
                thread.join()
        
    def __handle_connection(self, conn, addr) -> None:
        with conn: # ensures there is a connection
            print(f"New connection to {addr}")
            message = self.__receive(conn)
            print(f"recieved message from {addr}: {message}")
            

    def __receive(self, conn):
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
        


if __name__ == '__main__':
    server = Server()
    server.run()