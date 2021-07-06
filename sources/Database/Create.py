import User
import json
from json import JSONDecodeError
from typing import List, Dict

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
