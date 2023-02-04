
import sys
import socket

class Client:

    def __init__(self, host='localhost', port=8080) -> None:
        self.host = host
        self.port = port

    def run(self) -> None:
        # this is the main loop of our client connection
        self.s = socket.socket()
        try:
            self.s.connect((self.host, self.port))

            ############# must authenticate first

            while True:
                request = self.__readInput()
                if request != 'close':
                    self.__send(request)

                elif request == 'close':
                    self.__close()
                    break

        except Exception as e:
            print(f'Error code {e.args[0]}, {e.args[1]}')
            self.__close()
        except KeyboardInterrupt:
            self.__close()


    def __readInput(self) -> str:
        userinput = input('SFS-Shell: ')
        return userinput

    def __sendToken(self) -> None:
        # todo
        pass

    def __send(self, data) -> None:
        # print(f'Sending message {data}')
        self.s.send(data.encode('utf-8'))
        self.s.send(b'\r\n')
    
    def __receive(self) -> str:
        # todo
        pass

    def __close(self) -> None:
        self.s.close()
        print("Closing client application...")
    

if __name__ == '__main__':
    client = Client()
    client.run()
    