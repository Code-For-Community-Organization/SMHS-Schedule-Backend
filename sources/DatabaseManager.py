from base64 import decode
from dataclasses import dataclass
from cryptography.fernet import Fernet
import json
from json import JSONDecodeError
from typing import List
import os

debug = True
if 'ON_HEROKU' in os.environ:
    debug = False

@dataclass
class User:
    email: str
    password: str

class DatabaseManager:
    def __init__(self):
        if debug:
            self.databaseName = 'debug-database.json'
            key = Fernet.generate_key()
        else:
            self.databaseName = 'production-database.json'
            key = str.encode(os.environ['CRYPTO_KEY'])
        self.cipherSuite = Fernet(key)

    def encodeCipher(self, data: str) -> str:
        encrypted = self.cipherSuite.encrypt(str.encode(data))
        cipherString = encrypted.decode("utf-8")
        return cipherString

    def decodeCipher(self, data: str) -> str:
        decrypted = self.cipherSuite.decrypt(str.encode(data))
        cipherString = decrypted.decode("utf-8")
        return cipherString
    
    def containsDuplicates(self, dbJSON, email: str) -> bool:
        doesContain = False

        for user in dbJSON:
            if self.decodeCipher(user['email']) == email:
                doesContain = True
        return doesContain

    def newUserEntry(self, user: User):
        with open(self.databaseName, "a+") as db:
            db.seek(0)
            cipherEmail = self.encodeCipher(data=user.email)
            cipherPassword = self.encodeCipher(data=user.password)
            newUser = {'email': cipherEmail, 'password': cipherPassword}
            try:
                #DB already exists
                dbJSON: List[dict[str, str]] = json.load(db)

                #Append new user if its email does not already exist
                if not self.containsDuplicates(dbJSON, email=user.email):
                    dbJSON.append(newUser)
    
                db.truncate(0) #Wipe file content
                db.seek(0) #Move file pointer to beginning
                json.dump(dbJSON, db)

            except JSONDecodeError:
                #DB does not exist, create new
                dbJSON: List[dict[str, str]] = [newUser]
                json.dump(dbJSON, db)
            
    def getUserEntry(self, email: str) -> User:
        #Open DB in read mode
        with open(self.databaseName, "r") as db:
            #Load JSON
            dbJSON = json.load(db)
            #Filter for matching email
            matchingUser = filter(lambda u: self.decodeCipher(u['email']) == email, dbJSON)
            #Decrypt information
            firstMatch = next(matchingUser)
            decryptedEmail = self.decodeCipher(firstMatch['email'])
            decryptedPassword = self.decodeCipher(firstMatch['password'])
            #Construct user
            targetUser = User(email=decryptedEmail, password=decryptedPassword)
            #return user
            return targetUser

if __name__ == "__main__":   
    databaseManager = DatabaseManager()
    newUser = User(email="fdsf@sm.org", password="696969")
    newUser2 = User(email="maojingen@smhsstudents.orgk", password="0123")
    databaseManager.newUserEntry(user=newUser)
    databaseManager.newUserEntry(user=newUser2)
    print(databaseManager.getUserEntry(email="maojingen@smhsstudents.orgk"))
