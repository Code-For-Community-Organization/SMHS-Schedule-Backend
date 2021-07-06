from base64 import decode
from dataclasses import dataclass
from cryptography.fernet import Fernet, InvalidToken
import json
from json import JSONDecodeError
from typing import Dict, List, Optional, NewType
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
            key = b'udmMAqGywVOeu1JXjAt3jc2UsjgoVhoGXBPXbR1ALYE='
        else:
            self.databaseName = 'production-database.json'
            if os.environ.get('CRYPTO_KEY') is not None:
                key = str.encode()
            else:
                raise NameError("Environment variable for crypto key is not found on server.")

        self.cipherSuite = Fernet(key)

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

    def newUserEntry(self, user: User):
        if not self.isValid(user):
            raise ValueError("Empty username or password is not allowed.")
        with open(self.databaseName, "a+") as db:
            db.seek(0)
            cipherEmail = self.encodeCipher(data=user.email)
            cipherPassword = self.encodeCipher(data=user.password)
            if cipherEmail is not None and cipherPassword is not None:
                newUser = {'email': cipherEmail, 'password': cipherPassword}
                try:
                    #DB already exists
                    dbJSON: List[Dict[str, str]] = json.load(db)

                    #Append new user if its email does not already exist
                    if not self.containsDuplicates(dbJSON, email=user.email):
                        dbJSON.append(newUser)
        
                    db.truncate(0) #Wipe file content
                    db.seek(0) #Move file pointer to beginning
                    json.dump(dbJSON, db)

                except JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    #DB does not exist, create new
                    dbJSON: List[Dict[str, str]] = [newUser]
                    json.dump(dbJSON, db)
            else:
                raise TypeError("While encoding email and/or password, it returned a None value.")

    def isValid(self, user: User) -> bool:
        if user.email == '' or user.password == '':
            return False
        else:
            return True

    def getUserEntry(self, email: str) -> Optional[User]:
        if email == '':
            return None
        #Open DB in read mode
        with open(self.databaseName, "r") as db:
            #Load JSON
            dbJSON = json.load(db)
            try:
                #Filter for matching email
                matchingUser = filter(lambda u: self.decodeCipher(u['email']) == email, dbJSON)
                firstMatch: Optional[Dict] = next(matchingUser)

                if firstMatch is not None:
                    #Decrypt information
                    decryptedEmail = self.decodeCipher(firstMatch['email'])
                    decryptedPassword = self.decodeCipher(firstMatch['password'])
                    if decryptedPassword is not None and decryptedEmail is not None:
                        #Construct user
                        targetUser = User(email=decryptedEmail, password=decryptedPassword)
                        #return user
                        return targetUser
                    else:
                        raise TypeError("While decoding email and/or password, it returned a None value.")
                else:
                    return None
            except InvalidToken as err:
                print(err)

    Successful = bool
    def deleteUserEntry(self, email: str) -> Successful:
        if email == '':
            return False
        #Open DB in read mode
        with open(self.databaseName, "r+") as db:
            #Load JSON
            dbJSON: List[Dict] = json.load(db)
            try:
                #Get list of indexes of matching email predicate
                userIndexes = [i for (i, n) in enumerate(dbJSON) if self.decodeCipher(n['email']) == email]

                #We only expect 1 item in list, get 1st index
                if userIndexes:
                    userIndex = userIndexes[0]
                else:
                    return False
                #Remove User at that index
                dbJSON.pop(userIndex)
                db.truncate(0) #Wipe file content
                db.seek(0) #Move file pointer to beginning
                json.dump(dbJSON, db)
                return True
            #Handle error where crypto token invalid
            except InvalidToken as err:
                print(err)
            
            #Handle error where index cannot be found in list
            except ValueError as err:
                print(err)
                return False

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
