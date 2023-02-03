import socket
from multiprocessing import Process

from serverConn import ServerConn

class Server:
    # https://docs.python.org/3/howto/sockets.html

    def __init__(self, port=8080) -> None:
        self.port = port
        self.conns = []

    def run(self) -> None:
        with socket.socket() as serversocket:
            serversocket.bind(('localhost', self.port))
            serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            serversocket.listen(2) # allow backlog of 2

            while True:
                conn, addr = serversocket.accept()
                self.conns.append(ServerConn(conn, addr))
                thread = Process(target=self.conns[-1].run(), args=(conn, addr,), daemon=True)
                thread.start()
                thread.join()
        

if __name__ == '__main__':
    server = Server()
    server.run()