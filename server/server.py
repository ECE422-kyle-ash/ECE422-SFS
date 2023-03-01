
import sys
import socket
import threading
import logging

from serverConn import ServerConn
from encryption import EncryptionHandler
from authenticator import Authenticator

class Server:

    def __init__(self, port=8080) -> None:
        self.port = port
        self.conns = []
        self.threads = []

    def run(self) -> None:
        thread = threading.Thread(target = self.listen, args=(), daemon=True)
        thread.start()
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

        def set_group(username,groupname):
            handler = EncryptionHandler()
            groups_file = handler.etc+'/groups'
            encrypted_username = handler.encrypt(username)
            encrypted_groupname = handler.encrypt(groupname)
            current_group = ""
            with open(groups_file) as f:
                lines = f.read().splitlines()
                for line in lines:
                    temp = line.split(" ")
                    if(temp[0] == encrypted_username):
                        current_group = temp[1]
            if not current_group:
                with open(groups_file,"a") as f:
                    f.write(encrypted_username+ " " + encrypted_groupname + " \n")
                f.close()
                return True
            old_line = encrypted_username + " " + current_group
            new_line = encrypted_username + " " + encrypted_groupname
            with open(groups_file, 'r') as f:
                fdata = f.read()
            fdata = fdata.replace(old_line,new_line)
            with open(groups_file,'w') as f:
                f.write(fdata)
            f.close()

        handler = EncryptionHandler()
        authenticator = Authenticator()
        while True:
            admin_input = input()
            if admin_input == 'add user':
                username = input('Username: ')
                if not authenticator.check_username(handler.encrypt(username)):
                    groupname = input('Groupname: ')
                    set_group(username, groupname)
                    print(f'{username} added to {groupname}')
                else:
                    print('User does not exist.')
            elif admin_input == 'add group':
                groupname = input('Groupname: ')
                # create group
                print(f'{groupname} created as group')

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
    