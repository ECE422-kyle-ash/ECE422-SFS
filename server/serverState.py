
import logging
from cryptography.fernet import Fernet
import os
import encryption
import re
class State:

    def run(self, server):
        return
    
class AuthenticateState(State):

    def run(self, server):
        # logging.debug(f"entering auth state with client {server.addr}...")
        # do auth stuff

        # success
        server.state = MainState()
    
class ExchangeKeyState(State):

    def run(self, server):

        # generate a key and save it to a block cipher through fernet
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
    handler = encryption.EncryptionHandler()
    #for testing, assuming test user is looged in
    cwd = '/test'
    current_user = ""
    def run(self, server):
        try:
            # show client their current position in the SFS shell
            server.send(server.currentDir)

            # receive message from client
            message = server.receive()
            if message: # we have message
                logging.info(f"recieved message from {server.addr}: {message}")
            else: # client no longer responding
                server.close()
                return
            # parse message
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
            
            elif tokens[0] == 'download': # download file from server
                # 2 arguments
                print('download not implemented')
        except Exception:
            server.close()
        return

    def ls(self):
        path = os.getcwd()
        list = os.listdir(path)
        user_list = []
        for file in list:
            if file == 'etc':
                continue
            temp = path+'/'+ file
            if(self.check_permission(path)):
                user_list.append(self.handler.decrypt(file))
            else:
                user_list.append(file)
            return '\n'.join(user_list)
        
    def cd(self, dir):
        dir = self.handler.encryptPath(dir)
        abs = os.path.abspath(dir)
        if self.check_permission(abs) or not os.path.isdir(dir):
            return "path does not exist or you do not have permission to access it"
        os.chdir(dir)
        return "success"
        
    #returns true if user has access, also checks for injection attempts   
    def check_permission(self,path):
        #check if path is inside home dir
        regex = re.compile(self.handler.home)
        match = regex.match(path)
        if not match:
            return False
        #check permissiions file for file perms
        owner, perm = self.getFilePermAndOwner(path)
        if self.current_user == owner:
            return True
        if(perm == "internal"):
            return True
        #if set to group check if users in the same group
        if perm == "group":
            if(self.getgroup(self.current_user) == self.getgroup(owner)):
                return True
            return False
        return False
        
    def getFilePermAndOwner(self,path):
        perms_file = self.handler.etc+'/permissions'
        perm = ""
        owner = ""
        with open(perms_file) as f:
            lines = f.read().splitlines()
            for line in lines:
                temp = line.split(" ")
                if(temp[0] == path):
                    owner = temp[1]
                    perm = temp[2]
        return owner, perm
                
    def getgroup(self,userID):
        groups_file = self.handler.etc+'/groups'
        group = ""
        with open(groups_file) as f:
            lines = f.read().splitlines()
            for line in lines:
                temp = line.split(" ")
                if(temp[0] == userID):
                    group = temp[1]
        return group
        