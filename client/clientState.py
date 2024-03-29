
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import getpass

class State:

    def run(self, client):
        return

class LoginState(State):

    def run(self, client):
        command = input('Commands:\ncreate - Create a new user\nlogin - login to an existing account\n>')

        if command == 'create': # create new acc
            print('Fill in the following fields to create an account:')
            username = input('Username: ')
            pass1 = ''
            pass2 = ''
            while True:
                pass1 = getpass.getpass(prompt='Password: ')
                if len(pass1) == 0:
                    print('\nPassword field cannot be empty.\n')
                else:
                    pass2 = getpass.getpass(prompt='Confirm Password: ')
                    if pass1 == pass2:
                        break
                    else:
                        print('\nPasswords do not match, try again.\n')
            client.send(f'create {username} {pass1}')
            response = client.receive()
            if response == 'Create Success':
                self.login(client, username)
            else:
                print('\nUsername already exists.\n')

        elif command == 'login': # login to acc
            username = input('Username: ')
            password = getpass.getpass(prompt='Password: ')
            client.send(f'login {username} {password}')
            response = client.receive()
            if response == 'Login Success':
                response = client.receive()
                if response != 'integrity okay':
                    print(response)
                self.login(client, username)
            else:
                print('\nIncorrect username and/or password.\n')

    def login(self, client, username):
        print(f'Logged into SFS user: {username}...')
        client.state = MainState()
        print('\nWelcome to the SFS-Client!\nType \'menu\' for help.')

# This handles the initial key exchange between client and server
class ExchangeKeyState(State):

    def run(self, client):
        # generate a private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        # get the public key to give to the server
        public_key = private_key.public_key()
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        client.s.sendall(pem)

        # receive the key and assign it to a block cipher through fernet
        cypherkey = client.s.recv(2048)
        key = private_key.decrypt(
            cypherkey,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        client.fernet = Fernet(key)

        client.send('OK')
        if client.receive() == 'OK': # success
            # print("Key exchange succeeded")
            client.state = LoginState()
        else:
            print("Key exchange failed")
            client.close()

# This is the main loop of the client CLI and appliction
class MainState(State):

    menu = []

    def __init__(self):
        self.isReceiving = True
        self.menu.append('\nCommand menu:')
        self.menu.append('ls - list contents of working dir')
        self.menu.append('cd <dirName> - change the working dir')
        self.menu.append('cat <fileName> - print out the contents of a text file')
        self.menu.append('mkdir <dirName> - create a directory')
        self.menu.append('touch <fileName> - create an empty file')
        self.menu.append('echo <fileName> <file_contents> - append text to a text file')
        self.menu.append('rm <fileName> - delete a file')
        self.menu.append('rename <fileName> <new_fileName> - rename a file')
        self.menu.append('chmod <name> <permission> - change file/directory permissions\nvalid permissions types" [\'internal\', \'user\', \'group\']')
        self.menu.append('menu - display this menu')
        self.menu.append('exit - exit the SFS Shell\n')

    def print_menu(self):
        for item in self.menu:
            print(item)

    def run(self, client):
        if self.isReceiving: # grab response from server...
            try:
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
            except Exception:
                client.send('resend')
                return
        # get user input
        request = client.readInput()
        # determine desired request
        tokens = request.split(' ')
        if tokens[0] == 'ls': # show contends of dir
            # 1 token
            client.send(request)
            message = client.receive()
            if message != ' ':
                print(message)

        elif tokens[0] == 'cd': # change dir
            # 2 tokens
            if len(tokens) == 2:
                client.send(request)
                message = client.receive()
                if message != ' ':
                    print(message)
            else:
                print('Usage: cd <dirName>')
                self.isReceiving = False
                return

        elif tokens[0] == 'cat': # read file
            # 2 tokens
            if len(tokens)==2:
                client.send(request)
                response = client.receive()
                if response == 'cat fail':
                    print('insufficient access, file does not exist or file is empty')
                else:
                    print(response)
            else:
                print('Usage: cat <fileName>')
                self.isReceiving = False
                return

        elif tokens[0] == 'mkdir': # make dir
            # 2 tokens
            if len(tokens)==2:
                client.send(request)
                response = client.receive()
                if response == 'mkdir fail :(':
                    print('insufficient access or directory already exists')
            else:
                print('Usage: mkdir <dirName>')
                self.isReceiving = False
                return
        
        elif tokens[0] == 'touch':
            # 2 tokens
            if len(tokens)==2:
                client.send(request)
                response = client.receive()
                if response == 'touch fail':
                    print('insufficient access or file already exists')
            else:
                print('Usage: touch <fileName>')
                self.isReceiving = False
                return
        
        elif tokens[0] == 'echo':
            # atleast 3 tokens
            if len(tokens) > 2:
                client.send(request)
                response = client.receive()
                if response == 'echo fail':
                    print('insufficient access or file does not exist')
            else:
                print('Usage: echo <fileName> <text>')
                self.isReceiving = False
                return

        elif tokens[0] == 'rm': # remove file/directory
            # 2 tokens
            if len(tokens)==2:
                client.send(request)
                response = client.receive()
                if response == 'rm fail':
                    print('insufficient access or file does not exist')
            else:
                print('Usage: rm <fileName>')
                self.isReceiving = False
                return

        elif tokens[0] == 'rename': # rename file
            # 3 tokens
            if len(tokens)==3:
                client.send(request)
                response = client.receive()
                if response == 'rename fail':
                    print('insufficient access or file does not exist')
            else:
                print('Usage: rename <fileName> <newName>')
                self.isReceiving = False
                return

        elif tokens[0] == 'chmod':
            # 3 tokens
            if len(tokens) == 3:
                client.send(request)
                response = client.receive()
                if response == 'chmod fail':
                    print('insufficient access/permission or file/dir does not exist')
            else:
                print('Usage: chmod <name> <permission>')
                self.isReceiving = False
                return
            
        elif tokens[0] == 'menu':
            self.print_menu()
            self.isReceiving = False
            return

        # elif tokens[0] == 'send': # send file to server
        #     # 2 tokens
        #     if len(tokens) == 2:
        #         filepath = tokens[1].rstrip('/')
        #         # check if file exists
        #         if not os.path.isfile(filepath):
        #             print(f'No file found at: {os.path.abspath(filepath)}')
        #             self.isReceiving = False
        #             return
        #         # parse and send information to server
        #         filename = os.path.basename(filepath)
        #         client.send(f'{tokens[0]} {filename}') # sends server 'send <filename>'
        #         ack = client.receive() # get ack from server
        #         if ack == "sendOK": # okay to send file
        #             if not client.sendFile(filepath): # send the file to the server
        #                 print('File transfer failed')
        #             else:
        #                 print(f'Successfully sent file at {filepath} to server.')
        #         elif ack == "permission error": # user does not have write permissions
        #             print('Error: User does not have write permissions in this dir.')
        #         else: # should never happen
        #             print('Error: Unexpected message from server')
        #     else:
        #         print(f'Syntax: send <filename>')
        
        # elif tokens[0] == 'download': # download file from server
        #     # 2 tokens
        #     client.send(request)
        #     print('download not implemented')

        elif tokens[0] == 'exit':
            client.close()

        else:
            print(f'Command {request} not found.')
            self.isReceiving = False
            return

        self.isReceiving = True
        return
    