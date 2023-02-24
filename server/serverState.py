
import logging
from cryptography.fernet import Fernet

class State:

    def run(self, server):
        return
    
class AuthenticateState(State):

    def run(self, server):
        # logging.debug(f"entering auth state with client {server.addr}...")
        # do auth stuff

        # success
        server.state = MainState()

        return

# class LoginState(State): # not needed?

#     def run(self, server):
#         # login stuff
#         return

class ExchangeKeyState(State):

    def run(self, server):

        key = Fernet.generate_key()
        server.fernet = Fernet(key)

        server.conn.send(key)

        if server.receive() == "OK": # success
            logging.info(f"ExchangeKeyState Success with {server.addr}")
            server.send('OK')
            server.state = AuthenticateState()
        else:
            logging.error(f"ExchangeKeyState Failed with {server.addr}")
            server.send('ERROR')
            server.close()
    
class MainState(State):

    def run(self, server):
        try:
            # show client their current position in the SFS shell
            server.send(server.currentDir)

            message = server.receive()
            if message:
                logging.info(f"recieved message from {server.addr}: {message}")
                pass
            else: # client no longer responding
                server.close()
                return
            tokens = message.split(' ')
            if tokens[0] == 'ls': # show contends of dir
                # 1 token
                print('ls not implemented')

            elif tokens[0] == 'cd': # change dir
                # 2 tokens
                print('cd not implemented')

            elif tokens[0] == 'cat': # read file
                # 2 tokens
                print('cat not implemented')

            elif tokens[0] == 'mkdir': # make dir
                # 2 tokens
                print('mkdir not implemented')

            elif tokens[0] == 'rm': # remove file/directory
                # 2 tokens
                print('rm not implemented')

            elif tokens[0] == 'mv': # move or rename file/dir
                # 2 or 3 tokens
                print('mv not implemented')

            elif tokens[0] == 'send': # send file to server
                # if user has permission to write file here:
                server.send('sendOK')
                if not server.receiveFile(tokens[1]):
                    logging.error(f'Error: File not received')
            
            elif tokens[0] == 'get': # download file from server
                # 2 arguments
                print('get not implemented')
        except Exception:
            server.close()
        return