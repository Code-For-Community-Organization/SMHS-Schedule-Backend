from base64 import decode
from dataclasses import dataclass
from cryptography.fernet import Fernet, InvalidToken
from typing import Dict, List, Optional
import os
from User import User
import Create
import Delete
import Read

debug = True
if 'ON_HEROKU' in os.environ:
    debug = False

class DatabaseManager:
    def __init__(self):
        if debug:
            self.databaseName = 'debug-database.json'
            key = b'udmMAqGywVOeu1JXjAt3jc2UsjgoVhoGXBPXbR1ALYE='
        else:
            self.databaseName = 'production-database.json'
            if os.environ.get('CRYPTO_KEY') is not None:
                key = str.encode()
            else:
                raise NameError("Environment variable for crypto key is not found on server.")

        self.cipherSuite = Fernet(key)

    #---------------- Helper Methods ----------------
    def containsDuplicates(self, dbJSON, email: str) -> bool:
        doesContain = False

        for user in dbJSON:
            try:
                decodedEmail = self.decodeCipher(user['email'])
                if decodedEmail is not None:
                    if decodedEmail == email:
                        doesContain = True
                else:
                    raise TypeError("While decoding a email in database, it returned a None value.")
            except InvalidToken as err:
                print(err)
        return doesContain

    def isValid(self, user: User) -> bool:
        if user.email == '' or user.password == '':
            return False
        else:
            return True

    #---------------- CRUD Operation Methods ----------------
    #Instance method
    deleteUserEntry = Delete.deleteUserEntry

    #Instance method
    newUserEntry = Create.newUserEntry

    #Instance method
    getUserEntry = Read.getUserEntry

#---------------- Encoding and Decoding Data ----------------
    def encodeCipher(self, data: str) -> Optional[str]:
        try:
            encrypted = self.cipherSuite.encrypt(str.encode(data))
            cipherString = encrypted.decode("utf-8")
            return cipherString
        except TypeError:
            return None

    def decodeCipher(self, data: str) -> Optional[str]:
        try:
            decrypted = self.cipherSuite.decrypt(str.encode(data))
            cipherString = decrypted.decode("utf-8")
            return cipherString
        except TypeError:
            return None
    

if __name__ == "__main__":   
    databaseManager = DatabaseManager()
    try:
        newUser = User(email="fdsf@sm.org", password="%")
        newUser2 = User(email="s", password="1")
        databaseManager.newUserEntry(user=newUser)
        databaseManager.newUserEntry(user=newUser2)
        print(databaseManager.getUserEntry(email=""))
        print(databaseManager.deleteUserEntry("s"))

    except Exception as e:
        print(e)
