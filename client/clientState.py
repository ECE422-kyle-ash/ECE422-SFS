
import os
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

    def __init__(self):
        self.isReceiving = True

    def run(self, client):
        
        if self.isReceiving: # grab response from server...
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
        tokens = request.split(' ')
        if tokens[0] == 'ls': # show contends of dir
            # 1 token
            client.send(request)
            print('ls not implemented')

        elif tokens[0] == 'cd': # change dir
            # 2 tokens
            client.send(request)
            print('cd not implemented')

        elif tokens[0] == 'cat': # read file
            # 2 tokens
            client.send(request)
            print('cat not implemented')

        elif tokens[0] == 'mkdir': # make dir
            # 2 tokens
            client.send(request)
            print('mkdir not implemented')

        elif tokens[0] == 'rm': # remove file/directory
            # 2 tokens
            client.send(request)
            print('rm not implemented')

        elif tokens[0] == 'mv': # move or rename file/dir
            # 2 or 3 tokens
            client.send(request)
            print('mv not implemented')

        elif tokens[0] == 'send': # send file to server
            # 2 arguments
            if len(tokens) == 2:
                filepath = tokens[1].rstrip('/')
                # check if file exists
                if not os.path.isfile(filepath):
                    print(f'No file found at: {os.path.abspath(filepath)}')
                    self.isReceiving = False
                    return
                # parse and send information to server
                filename = os.path.basename(filepath)
                client.send(f'{tokens[0]} {filename}') # sends server 'send <filename>'
                ack = client.receive() # get ack from server
                if ack == "sendOK": # okay to send file
                    if not client.sendFile(filepath): # send the file to the server
                        print('File transfer failed')
                    else:
                        print(f'Successfully sent file at {filepath} to server.')
                elif ack == "permission error": # user does not have write permissions
                    print('Error: User does not have write permissions in this dir.')
                else: # should never happen
                    print('Error: Unexpected message from server')
            else:
                print(f'Improper use of send.\nSyntax: send <filename>')
        
        elif tokens[0] == 'get': # download file from server
            # 2 arguments
            client.send(request)
            print('get not implemented')

        elif tokens[0] == 'exit':
            client.close()

        else:
            print(f'Command {request} not found.')
            self.isReceiving = False
            return

        self.isReceiving = True
        return
    