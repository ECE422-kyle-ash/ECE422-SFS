
import sys
import socket
import threading
import logging

from serverConn import ServerConn
from encryption import EncryptionHandler

class Server:

    def __init__(self, port=8080) -> None:
        self.port = port
        self.conns = []
        self.threads = []

    def run(self) -> None:
        logging.info(f'Starting server on port: {self.port}')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serversocket:
            serversocket.bind(('localhost', self.port))
            serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            serversocket.listen()
            try:
                while True:
                    conn, addr = serversocket.accept()
                    self.__spawn(conn, addr)
            except KeyboardInterrupt:
                self.__close(serversocket)
    
    def __spawn(self, conn, addr):
        self.conns.append(ServerConn(conn, addr))
        thread = threading.Thread(target = self.conns[-1].run, args=(), daemon=True)
        self.threads.append(thread)
        thread.start()

    def listen(self):
        handler = EncryptionHandler()
        while True:
            admin_input = input()

    def __close(self, serversocket):
        for connection in self.conns:
            connection.close()
        serversocket.shutdown(socket.SHUT_RDWR)
        serversocket.close()
        logging.info("Server closed...")
        

if __name__ == '__main__':
    logging.basicConfig(level=logging.NOTSET)

    if len(sys.argv) == 2:
        port = sys.argv[1]
        server = Server(int(port))
    else:
        server = Server()
    server.run()
    