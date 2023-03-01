
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
import os
import encryption
import re
from simple_file_checksum import get_checksum
from checksumdir import dirhash
import bcrypt

from authenticator import Authenticator

class State:

    def run(self, server):
        return
    
class AuthenticateState(State):
    authenticator = Authenticator()
    handler = encryption.EncryptionHandler()

    def run(self, server):
        
        command = server.receive()
        tokens = command.split(' ')
        if tokens[0] == 'create':
            if (self.authenticator.create_user(tokens[1], tokens[2])):
                server.send('Create Success')
                # log user in
                self.login_user(server, tokens[1])
                return
            else:
                server.send('Create Failed')
        elif tokens[0] == 'login':
            if (self.authenticator.authenticate_user(tokens[1], tokens[2])):
                (check, files) = self.authenticator.check_integrity(self.handler.encrypt(tokens[1]))
                server.send('Login Success')
                if not check:
                    server.send('the following files and directories were modified\n'+"\n".join(files))
                else:
                    server.send('integrity okay')
                self.login_user(server, tokens[1])
                return
            else:
                server.send('Login Failed')
    
    def login_user(self, server, username):
        server.state = MainState()
        server.state.username = username
        server.state.current_user = self.handler.encrypt(username)
    
class ExchangeKeyState(State):

    def run(self, server):

        # get the clients public key
        pem = server.conn.recv(4096)
        public_key = serialization.load_pem_public_key(pem)

        # generate a key and save it to a block cipher through fernet
        key = Fernet.generate_key()
        server.fernet = Fernet(key)

        cipherkey = public_key.encrypt(
            key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        server.conn.send(cipherkey)

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
    username = ""
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

            # elif tokens[0] == 'send': # send file to server
            #     # if user has permission to write file here:
            #     server.send('sendOK')
            #     if not server.receiveFile(tokens[1]):
            #         logging.error(f'Error: File not received')
            
            # elif tokens[0] == 'download': # download file from server
            #     # 2 arguments
            #     print('download not implemented')
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
    
    def update_checksum(self,path):
        perms_file = self.handler.etc+'/permissions'
        owner, perm = self.getFilePermAndOwner(path)
        old_checksum = self.grab_checksum(path)
        new_checksum = get_checksum(path, algorithm="SHA256").decode()
        old_line = path+" "+owner+" "+perm+" "+old_checksum
        new_line = path+" "+owner+" "+perm+" "+new_checksum
        with open(perms_file, 'r') as f:
            fdata = f.read()
        fdata = fdata.replace(old_line,new_line)
        with open(perms_file,'w') as f:
            f.write(fdata)
        f.close()
    
    def update_checksum_dir(self,path):
        perms_file = self.handler.etc+'/permissions'
        owner, perm = self.getFilePermAndOwner(path)
        old_checksum = self.grab_checksum(path)
        new_checksum = dirhash(path, 'sha256').decode()
        old_line = path+" "+owner+" "+perm+" "+old_checksum
        new_line = path+" "+owner+" "+perm+" "+new_checksum
        with open(perms_file, 'r') as f:
            fdata = f.read()
        fdata = fdata.replace(old_line,new_line)
        with open(perms_file,'w') as f:
            f.write(fdata)
        f.close()
    
    def grab_checksum(self,path):
        perms_file = self.handler.etc+'/permissions'
        checksum = ""
        with open(perms_file) as f:
            lines = f.read().splitlines()
            for line in lines:
                temp = line.split(" ")
                if(temp[0] == path):
                    checksum = temp[3]
        return checksum
    # returns true, empty list if integrity check succeeded,  or false, list of decrypted file names whose integrity checks failed
    def check_integrity(self,userID):
        checkFailed = []
        perms_file = self.handler.etc+'/permissions'
        with open(perms_file) as f:
            lines = f.read().splitlines()
            for line in lines:
                temp = line.split(" ")
                if(temp[1] == userID):
                    path = temp[0]
                    if (not os.path.isfile(path) and not os.path.isdir(path)):
                        checkFailed.append(self.handler.decrypt(path.split("/")[-1]))
                    elif os.path.isfile(path):
                        if get_checksum(path, algorithm="SHA256").decode() != temp[3]:
                            checkFailed.append(self.handler.decrypt(path.split("/")[-1]))
                    elif os.path.isdir(path):
                        if dirhash(path, 'sha256').decode() != temp[3]:
                            checkFailed.append(self.handler.decrypt(path.split("/")[-1]))
        if not checkFailed:
            return True, checkFailed               
        return False ,checkFailed
    
    def set_group(self,username,groupname):
        groups_file = self.handler.etc+'/permissions'
        encrypted_username = self.handler.encrypt(username)
        encrypted_groupname = self.handler.encrypt(groupname)
        current_group = ""
        with open(groups_file) as f:
            lines = f.read().splitlines()
            for line in lines:
                temp = line.split(" ")
                if(temp[0] == encrypted_username):
                    current_group = temp[1]
        if not current_group:
            with open(groups_file,"a") as f:
                f.write(encrypted_username+ " " + encrypted_groupname + " \n")
            f.close()
            return True
        old_line = encrypted_username + " " + current_group
        new_line = encrypted_username + " " + encrypted_groupname
        with open(groups_file, 'r') as f:
            fdata = f.read()
        fdata = fdata.replace(old_line,new_line)
        with open(groups_file,'w') as f:
            f.write(fdata)
        f.close()
    
    def mkdir(self, name):
        dir = self.handler.encryptPath(dir)
        abs = os.path.abspath(dir)
        if self.check_permission(abs) and not os.path.isdir(abs):
            os.makedirs(abs)
            perms_file = self.handler.etc+'/permissions'
            with open(perms_file,"a") as f:
                f.write(dir+ " " + self.current_user + " "+ "user" + " " + dirhash(abs, 'sha256').decode() + " \n")
            f.close()
            return True
        return False
    
    
            
    
    def touch(self, name):
        pass
    
    def rename(self, current_name, new_name):
        pass
    
    def rm(self, fname):
        pass
    
    def chmod(self, fname, new_perm):
        pass
    
    def echo(self, fname):
        pass
        
        
                    

    