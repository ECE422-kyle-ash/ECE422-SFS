
import sys
import socket

from state import State
from mainState import MainState
from authenticateState import AuthenticateState
from loginState import LoginState
from exchangeKeyState import ExchangeKeyState

BUFFER_SIZE = 1024

class Client:

    def __init__(self, host='localhost', port=8080) -> None:
        self.host = host
        self.port = port
        self.currentDir = ''
        self.state = State()
        self.isClosed = False

    def run(self) -> None:
        # this is the main loop of our client connection
        self.s = socket.socket()
        try:
            self.s.connect((self.host, self.port))

            ############# must authenticate first

            # go main state
            self.state = MainState()

            while not self.isClosed:
                self.state.run(client=self)

        except Exception as e:
            print(f'Error code {e.args[0]}, {e.args[1]}')
            self.close()
        except KeyboardInterrupt:
            print("\nKeyboard Interrupt Detected...")
            self.close()


    def readInput(self) -> str:
        userinput = input(f'{self.currentDir}$ ')
        return userinput

    def sendToken(self) -> None:
        # todo
        pass

    def send(self, data) -> None:
        self.s.send(data.encode('utf-8'))
    
    def receive(self) -> str:
        data = self.s.recv(BUFFER_SIZE)
        if not data:
            return
        message = data.decode('utf-8')
        return message

    def close(self) -> None:
        self.s.close()
        self.isClosed = True
        print("Closing client application...")
    

if __name__ == '__main__':
    if len(sys.argv) == 3:
        host = sys.argv[1]
        port = sys.argv[2]
        client = Client(host = host, port = int(port))
    else:
        client = Client()
    client.run()
    