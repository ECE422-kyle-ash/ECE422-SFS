
from cryptography.fernet import Fernet

class State:

    def run(self, client):
        return

# class AuthenticateState(State): # not needed?

#     def run(self, client):
#         # do auth stuff
#         return

class LoginState(State):

    def run(self, client):
        # print(f"entering login state...")
        # login stuff

        #success
        client.state = MainState()
        return

class ExchangeKeyState(State):

    def run(self, client):

        key = client.s.recv(1024)
        client.fernet = Fernet(key)

        client.send('OK')
        if client.receive() == 'OK': # success
            print("Key exchange succeeded")
            client.state = LoginState()
        else:
            print("Key exchange failed")
            client.close()

class MainState(State):

    def run(self, client):
        # grab current dir
        message = client.receive()
        if message == None: # server has closed connection
            print('Error: Connection to server lost')
            client.close()
            return
        elif message.__contains__('Shell'):
            client.currentDir = message
        else: # something has gone wrong
            print('Error: Unexpected message from server')
            client.close()
            return

        # get user input
        request = client.readInput()
        # determine desired request
        if request != 'exit':
            client.send(request)

        elif request == 'exit':
            client.close()

        return
    