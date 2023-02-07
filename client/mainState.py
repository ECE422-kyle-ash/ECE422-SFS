
from state import State

class MainState(State):

    def run(self, client):
        while True:
            # grab current dir
            message = client.receive()
            if message.__contains__('Shell'):
                client.currentDir = message
            elif message == None: # Server socket is dead
                print('Error: Nothing recieved from server')
                client.close()
                return
            else: # something has gone wrong
                print('Error: Unexpected message from server')
                client.close()
                return


            request = client.readInput()
            if request != 'exit':
                client.send(request)

            elif request == 'exit':
                client.close()
                return client
    