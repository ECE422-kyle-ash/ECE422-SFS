
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
        except Exception:
            server.close()
        return