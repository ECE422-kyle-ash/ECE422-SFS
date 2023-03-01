import encryption
import bcrypt

class Authenticator:

    def __init__(self) -> None:
        self.handler = encryption.EncryptionHandler()

    def create_user(self, username, password):
        users_file = self.handler.etc+'/users'
        encrypted_username = self.handler.encrypt(username)
        hashed_pw = bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()
        if self.check_username(encrypted_username):
            with open(users_file,"a") as f:
                f.write(encrypted_username+ " " + hashed_pw + " \n")
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
    