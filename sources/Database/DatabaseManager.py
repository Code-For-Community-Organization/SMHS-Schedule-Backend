from cryptography.fernet import Fernet, InvalidToken
from typing import Optional, Dict, List
import os
import json
from json import JSONDecodeError

if __name__ == "__main":
    from User import User
else:
    from .User import User

debug = True
if 'ON_HEROKU' in os.environ:
    debug = False

#typealias
jsonDB = List[Dict[str, str]]

class DatabaseManager:
    def __init__(self):
        if debug:
            self.databaseName = 'debug-database.json'
            key = b'udmMAqGywVOeu1JXjAt3jc2UsjgoVhoGXBPXbR1ALYE='
        else:
            self.databaseName = 'production-database.json'
            serverKey: Optional[str] = os.environ.get('CRYPTO_KEY')
            if serverKey is not None:
                key: bytes = str.encode(serverKey)
            else:
                raise NameError(
                    "Environment variable for crypto key is not found on server.")

        self.cipherSuite = Fernet(key)

    # ---------------- Helper Methods ----------------
    def _containsDuplicates(self, dbJSON: jsonDB, email: str) -> bool:
        doesContain = False
        for user in dbJSON:
            try:
                decodedEmail = self._decodeCipher(user['email'])
                if decodedEmail is not None:
                    if decodedEmail == email:
                        doesContain = True
                else:
                    raise TypeError(
                        "While decoding a email in database, it returned a None value.")
            except InvalidToken as err:
                print(err)
        return doesContain

    def _isValid(self, user: User) -> bool:
        if user.email == '' or user.password == '':
            return False
        else:
            return True

    # ---------------- CRUD Operation Methods ----------------
    # Instance method
    Successful = bool

    def deleteUserEntry(self, email: str) -> Successful:
        if email == '':
            return False
        # Open DB in read mode
        with open(self.databaseName, "r+") as db:
            # Load JSON
            dbJSON: jsonDB = json.load(db)
            try:
                # Get list of indexes of matching email predicate
                userIndexes = [i for (i, n) in enumerate(
                    dbJSON) if self._decodeCipher(n['email']) == email]

                # We only expect 1 item in list, get 1st index
                if userIndexes:
                    userIndex = userIndexes[0]
                else:
                    return False
                # Remove User at that index
                dbJSON.pop(userIndex)
                db.truncate(0)  # Wipe file content
                db.seek(0)  # Move file pointer to beginning
                json.dump(dbJSON, db)
                return True
            # Handle error where crypto token invalid
            except InvalidToken as err:
                print(err)

            # Handle error where index cannot be found in list
            except ValueError as err:
                print(err)
            return False

    # Instance method
    def newUserEntry(self, user: User):
        if not self._isValid(user):
            raise ValueError("Empty username or password is not allowed.")
        with open(self.databaseName, "a+") as db:
            db.seek(0)
            cipherEmail = self._encodeCipher(data=user.email)
            cipherPassword = self._encodeCipher(data=user.password)
            if cipherEmail is not None and cipherPassword is not None:
                newUser = {'email': cipherEmail, 'password': cipherPassword}
                try:
                    # DB already exists
                    dbJSON: jsonDB = json.load(db)

                    # Append new user if its email does not already exist
                    if not self._containsDuplicates(dbJSON, email=user.email):
                        dbJSON.append(newUser)

                    db.truncate(0)  # Wipe file content
                    db.seek(0)  # Move file pointer to beginning
                    json.dump(dbJSON, db)

                except JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    # DB does not exist, create new
                    dbJSON: jsonDB = [newUser]
                    json.dump(dbJSON, db)
            else:
                raise TypeError(
                    "While encoding email and/or password, it returned a None value.")

    # Instance method

    def getUserEntry(self, email: str) -> Optional[User]:
        if email == '':
            return None
        # Open DB in read mode
        with open(self.databaseName, "r") as db:
            # Load JSON
            dbJSON = json.load(db)
            try:
                # Filter for matching email
                matchingUser = filter(lambda u: self._decodeCipher(
                    u['email']) == email, dbJSON)
                firstMatch: Optional[Dict[str, str]] = next(matchingUser)

                if firstMatch is not None:
                    # Decrypt information
                    decryptedEmail = self._decodeCipher(firstMatch['email'])
                    decryptedPassword = self._decodeCipher(
                        firstMatch['password'])
                    if decryptedPassword is not None and decryptedEmail is not None:
                        # Construct user
                        targetUser = User(email=decryptedEmail,
                                          password=decryptedPassword)
                        # return user
                        return targetUser
                    else:
                        raise TypeError(
                            "While decoding email and/or password, it returned a None value.")
                else:
                    return None
            except InvalidToken as err:
                print(err)

# ---------------- Encoding and Decoding Data ----------------
    def _encodeCipher(self, data: str) -> Optional[str]:
        try:
            encrypted = self.cipherSuite.encrypt(str.encode(data))
            cipherString = encrypted.decode("utf-8")
            return cipherString
        except TypeError:
            return None

    def _decodeCipher(self, data: str) -> Optional[str]:
        try:
            decrypted = self.cipherSuite.decrypt(str.encode(data))
            cipherString = decrypted.decode("utf-8")
            return cipherString
        except TypeError:
            return None


if __name__ == "__main__":
    databaseManager1 = DatabaseManager()
    databaseManager2 = DatabaseManager()
    try:
        newUser = User(email="fdsf@smhst.org", password="%")
        newUser2 = User(email="s", password="1")
        databaseManager1.newUserEntry(user=newUser)
        databaseManager2.newUserEntry(user=newUser2)
        print(databaseManager1.getUserEntry(email="s"))
        print(databaseManager2.getUserEntry(email="s"))

    except Exception as e:
        print(e)
