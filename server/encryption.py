from cryptography.fernet import Fernet
import encryption
import os
class EncryptionHandler:
    def __init__(self) -> None:
        self.key = b'uH7165Y3br4X2CyRKNXH_ENLHESfsEnNKYD2fz3xtBk='
        self.fernet = Fernet(self.key)
        self.realpath = os.path.dirname(os.path.realpath(__file__))
        self.home = self.realpath+'/home'
        self.etc = self.home+'/etc'
    
    #returns string of encrypted text string
    def encrypt(self,text):
        return self.fernet.encrypt(text.encode()).decode()
    
    #returns string of decrypted text string
    def decrypt(self,text):
        return self.fernet.decrypt(text.encode()).decode()
    
    def encryptPath(self, path):
        directories = path.split("/")
        encrypted = []
        for directory in directories:
            if directory == ''or directory == 'home':
                continue
            if directory != '..' and directory != '.':
                directory = self.encrypt(directory)
            encrypted.append(directory)

        return "/".join(encrypted)

    def decryptPath(self, key, path):
        directories = path.split("/")
        decrypted = []
        for directory in directories:
            if directory == ''or directory == 'home':
                continue
            if directory != '..' and directory != '.':
                directory = self.decrypt(directory)
            decrypted.append(directory)

        return "/".join(decrypted)

    def getEncryptedPath(self, path):
        directories = path.split("/")
        encrypted = []
        for directory in directories:
            if directory == '' or directory == 'home':
                continue
            if directory != '..' and directory != '.':
                directory = self.encrypt(directory)
            encrypted.append(directory)

        return self.home + "/".join(encrypted)

    def getDecryptedPath(self, key, path):
        directories = path.split("/")
        decrypted = []
        for directory in directories:
            if directory == '' or directory == 'home':
                continue
            if directory != '..' and directory != '.':
                directory = self.decrypt(directory)
            decrypted.append(directory)

        return self.home +"/".join(decrypted)