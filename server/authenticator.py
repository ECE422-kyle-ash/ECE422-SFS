import encryption
import bcrypt
import os
from checksumdir import dirhash
from simple_file_checksum import get_checksum
class Authenticator:

    def __init__(self) -> None:
        self.handler = encryption.EncryptionHandler()

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
                        if get_checksum(path, algorithm="SHA256") != temp[3]:
                            checkFailed.append(self.handler.decrypt(path.split("/")[-1]))
                    elif os.path.isdir(path):
                        if dirhash(path, 'sha256') != temp[3]:
                            checkFailed.append(self.handler.decrypt(path.split("/")[-1]))
        if not checkFailed:
            return True, checkFailed               
        return False ,checkFailed
    
    def create_user(self, username, password):
        users_file = self.handler.etc+'/users'
        encrypted_username = self.handler.encrypt(username)
        hashed_pw = bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()
        if self.check_username(encrypted_username):
            with open(users_file,"a") as f:
                f.write(encrypted_username+ " " + hashed_pw + " \n")
            f.close()       
            os.makedirs(self.handler.home+"/"+encrypted_username)
            perms_file = self.handler.etc+'/permissions'
            with open(perms_file,"a") as f:
                f.write(self.handler.home+"/"+encrypted_username+ " " + encrypted_username + " "+ "group" + " " + dirhash(self.handler.home+"/"+encrypted_username, 'sha256') + " \n")
            f.close()
            return True
        return False
    
    def check_username(self,username_encrypted):
        users_file = self.handler.etc+'/users'
        with open(users_file) as f:
            lines = f.read().splitlines()
            for line in lines:
                temp = line.split(" ")
                if(temp[0] == username_encrypted):
                    return False
        return True
    
    #return true if username, password exist, false otherwise
    def authenticate_user(self, username, password):
        users_file = self.handler.etc+'/users'
        username_encrypted = self.handler.encrypt(username)
        with open(users_file) as f:
            lines = f.read().splitlines()
            for line in lines:
                temp = line.split(" ")
                if(temp[0] == username_encrypted and bcrypt.checkpw(password.encode(), temp[1].encode())):
                    return True
        return False
    