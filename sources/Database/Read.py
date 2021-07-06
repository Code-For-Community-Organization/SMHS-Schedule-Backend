from typing import Optional
from User import User
from cryptography.fernet import InvalidToken

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