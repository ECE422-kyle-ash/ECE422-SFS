
import sys
import socket

BUFFER_SIZE = 1024

class Client:

    def __init__(self, host='localhost', port=8080) -> None:
        self.host = host
        self.port = port
        self.currentDir = ''

    def run(self) -> None:
        # this is the main loop of our client connection
        self.s = socket.socket()
        try:
            self.s.connect((self.host, self.port))

            ############# must authenticate first

            while True:
                # grab current dir
                message = self.__receive()
                if message.__contains__('Shell'):
                    self.currentDir = message
                elif message == None: # Server socket is dead
                    print('Error: Nothing recieved from server')
                    self.__close()
                    return
                else: # something has gone wrong
                    print('Error: Unexpected message from server')
                    self.__close()
                    return


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
        userinput = input(f'{self.currentDir}$ ')
        return userinput

    def __sendToken(self) -> None:
        # todo
        pass

    def __send(self, data) -> None:
        self.s.send(data.encode('utf-8'))
    
    def __receive(self) -> str:
        data = self.s.recv(BUFFER_SIZE)
        if not data:
            return
        message = data.decode('utf-8')
        return message

    def __close(self) -> None:
        self.s.close()
        print("Closing client application...")
    

if __name__ == '__main__':
    if len(sys.argv) == 2:
        port = sys.argv[1]
        client = Client(int(port))
    else:
        client = Client()
    client.run()
    