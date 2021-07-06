import json
from cryptography.fernet import InvalidToken
from typing import Dict, List

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