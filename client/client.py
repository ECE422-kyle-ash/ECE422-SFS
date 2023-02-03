import socket

class Client:

    def __init__(self, host='localhost', port=8080) -> None:
        self.host = host
        self.port = port

    def run(self):
        with socket.socket() as self.s:
            self.s.connect((self.host, self.port))
            self.__send(b'hello server')

            self.s.close()

    def __send(self, data):
        print(f'Sending message {data}')
        self.s.send(data)
    

if __name__ == '__main__':
    client = Client()
    client.run()