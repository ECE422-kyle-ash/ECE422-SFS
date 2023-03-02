
import sys
import socket

from clientState import State
from clientState import MainState
# from clientState import AuthenticateState
from clientState import LoginState
from clientState import ExchangeKeyState

BUFFER_SIZE = 4096

class Client:

    def __init__(self, host='localhost', port=8080) -> None:
        self.host = host
        self.port = port
        self.currentDir = ''
        self.state = State()
        self.isClosed = False
        self.privateKey = ''
        self.publicKey = ''
        self.fernet = None

    def run(self) -> None:
        # this is the main loop of our client connection
        self.s = socket.socket()
        print(f"Connecting to {self.host} on port {self.port}...")
        try:
            self.s.connect((self.host, self.port))
            self.s.settimeout(5)

            self.state = ExchangeKeyState()

            while not self.isClosed:
                self.state.run(client=self)

        # except Exception as e:
        #     print(f'Error code {e}')
        #     self.close()
        except KeyboardInterrupt:
            print("\nKeyboard Interrupt Detected...")
            self.close()


    def readInput(self) -> str:
        userinput = input(f'{self.currentDir}$ ')
        return userinput

    def send(self, data) -> None:
        crypto = self.fernet.encrypt(data.encode('utf-8'))
        self.s.send(crypto)
    
    def receive(self) -> str:
        data = self.s.recv(BUFFER_SIZE)
        if not data:
            return
        message = self.fernet.decrypt(data).decode('utf-8')
        return message

    # def sendFile(self, filepath: str) -> bool:
    #     with open(filepath, 'rb') as f:
    #         while True:
    #             data = f.read(1024)
    #             if not data:
    #                 break
    #             crypto = self.fernet.encrypt(data)
    #             # print(f'data: {len(data)} crpyto: {len(crypto)}')
    #             self.s.send(crypto)
    #             try:
    #                 if not self.receive() == 'OK':
    #                     print('Unexpected response from server')
    #                     self.close()
    #                     return False
    #             except:
    #                 print('Error: No response from Server')
    #                 return False
    #         crypto = self.fernet.encrypt(b'\04')
    #         self.s.send(crypto)
    #         try:
    #             if self.receive() == 'EOFOK':
    #                 return True
    #             else:
    #                 print('Unexpected response from server')
    #                 self.close()
    #                 return False
    #         except:
    #             print('Error: No response from Server')
    #             return False

    def close(self) -> None:
        self.s.close()
        self.isClosed = True
        print("Closing client application...")
    

if __name__ == '__main__':
    if len(sys.argv) == 3:
        host = sys.argv[1]
        port = sys.argv[2]
        client = Client(host = host, port = int(port))
    elif len(sys.argv) == 2:
        port = sys.argv[1]
        client = Client( port = int(port))
    else:
        client = Client()
    client.run()
    