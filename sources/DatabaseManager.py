from cryptography.fernet import Fernet, InvalidToken
from typing import Optional, Dict, List, Any, overload
import os
import json
from json import JSONDecodeError
if __name__ == "__main__":
    from AeriesScraper import Period, PeriodEncoder
    from Student import Student
else:
    from .Student import Student
    from .AeriesScraper import Period, PeriodEncoder
import sys

debug = False
if 'ON_HEROKU' in os.environ:
    print("DEBUG FALSE")
    sys.stdout.flush()
    debug = False

# typealias
# Describes an array of dictionary, each containing
# a key of type string, and a value of either type
# string, or a dictionary with key and value of type string
jsonDB = List[Dict[str, Any]]


class DatabaseManager:
    def __init__(self):
        if debug:
            print("debug database name used")
            sys.stdout.flush()
            self.databaseName = 'debug-database.json'
            key = b'udmMAqGywVOeu1JXjAt3jc2UsjgoVhoGXBPXbR1ALYE='
        else:
            print("Production database name used")
            sys.stdout.flush()
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
                if debug:
                    print(err)
                    sys.stdout.flush()
        return doesContain

    def _isValid(self, user: Student) -> bool:
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
                if debug:
                    print(err)
                    sys.stdout.flush()

            # Handle error where index cannot be found in list
            except ValueError as err:
                if debug:
                    print(err)
                    sys.stdout.flush()

            return False

    # Instance method - Create new user
    def newUserEntry(self, user: Student):
        if not self._isValid(user):
            raise ValueError("Empty username or password is not allowed.")
        with open(self.databaseName, "a+") as db:
            db.seek(0)
            cipherEmail = self._encodeCipher(data=user.email)
            cipherPassword = self._encodeCipher(data=user.password)
            if cipherEmail is not None and cipherPassword is not None:
                newUser = {'email': cipherEmail,
                           'password': cipherPassword,
                           'grades': self._newUserGradesEntry(periods=user.grades),
                           'lastUpdated': user.lastUpdated}
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
                    if debug:
                        print(f"Error decoding JSON: {e}")
                        sys.stdout.flush()

                    # DB does not exist, create new
                    dbJSON: jsonDB = [newUser]
                    json.dump(dbJSON, db)
            else:
                raise TypeError(
                    "While encoding email and/or password, it returned a None value.")

    # Instance method - Help construct user's grades data
    def _newUserGradesEntry(self, periods: List[Period]) -> List[Dict[str, Any]]:
        periodGrades: List[Dict[str, Any]] = []
        for period in periods:
            jsonFormat = PeriodEncoder().encode(period)
            dictFormat = json.loads(jsonFormat)
            periodGrades.append(dictFormat)
        return periodGrades

    def getUserEntry(self, email: str) -> Optional[Dict[str, Any]]:
        if email == '':
            return None
        # Open DB in read mode
        with open(self.databaseName, "a+") as db:
            db.seek(0)
            try:
                # Load JSON
                dbJSON = json.load(db)
                # Filter for matching email
                matchingUser = filter(lambda u: self._decodeCipher(
                    u['email']) == email, dbJSON)
                firstMatch: Optional[Dict[str, Any]] = next(matchingUser)

                if firstMatch is not None:
                    # Decrypt information
                    decryptedEmail = self._decodeCipher(firstMatch['email'])
                    decryptedPassword = self._decodeCipher(
                        firstMatch['password'])
                    if decryptedPassword is not None and decryptedEmail is not None:
                        # Reassign email and password with decoded data
                        firstMatch['email'] = decryptedEmail
                        firstMatch['password'] = decryptedPassword
                        # return user
                        return firstMatch
                    else:
                        raise TypeError(
                            "While decoding email and/or password, it returned a None value.")
                else:
                    return None
            except JSONDecodeError as err:
                if debug:
                    print(err)
                    sys.stdout.flush()

            except InvalidToken as err:
                if debug:
                    print(err)
                    sys.stdout.flush()

            except StopIteration as err:
                if debug:
                    print(err)
                    sys.stdout.flush()

    def getUserGrades(self, email: str) -> Optional[List[Dict[str, Any]]]:
        try:
            entry = self.getUserEntry(email)
            if entry is not None:
                # Construct user object
                return entry['grades']
            else:
                return None
        except (TypeError, InvalidToken) as err:
            if debug:
                print(err)
                sys.stdout.flush()

            return None

    # Instance method
    def getUserEntryObject(self, email: str) -> Optional[Student]:
        try:
            entry = self.getUserEntry(email)
            if entry is not None:
                # Construct user object
                return Student(email=entry['email'],
                               password=entry['password'],
                               grades=Period.convertToPeriods(entry['grades']))
            else:
                return None
        except (TypeError, InvalidToken) as err:
            if debug:
                print(err)
                sys.stdout.flush()

            return None

    def getAllUserEntryObjects(self) -> Optional[List[Student]]:
        # Initialize empty list for all entries
        allStudents: List[Student] = []
        with open(self.databaseName, "a+") as db:
            db.seek(0)
            try:
                # Load JSON
                dbJSON: jsonDB = json.load(db)
                for student in dbJSON:
                    # Decrypt information
                    decryptedEmail = self._decodeCipher(student['email'])
                    decryptedPassword = self._decodeCipher(student['password'])
                    if decryptedPassword is not None and decryptedEmail is not None:
                        # Reassign email and password with decoded data
                        student['email'] = decryptedEmail
                        student['password'] = decryptedPassword

                        #Construct new Student object from our information
                        studentEntry = Student(decryptedEmail,
                                               decryptedPassword,
                                               student['grades'],
                                               lastUpdated=student['lastUpdated'])

                        allStudents.append(studentEntry)
                    else:
                        raise TypeError(
                            "While decoding email and/or password, it returned a None value.")
            except JSONDecodeError as err:
                print("getAllUserEntryObjects", err)
                sys.stdout.flush()

            except InvalidToken as err:
                print(err)
                sys.stdout.flush()

        return allStudents
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
        testPeriod1 = Period(periodNum=1,
                             periodName="English",
                             teacherName="Donald",
                             gradePercent=98.3,
                             currentMark="A",
                             isPrior=False)
        testPeriod2 = Period(periodNum=2,
                             periodName="Algebra 1",
                             teacherName="Biden",
                             gradePercent=93.5,
                             currentMark="A-",
                             isPrior=False)
        newUser = Student(email="fdsf@smhst.org", password="%",
                          grades=[testPeriod1, testPeriod2])
        newUser2 = Student(email="s", password="1", grades=[
            testPeriod2, testPeriod1])
        databaseManager1.newUserEntry(user=newUser)
        databaseManager2.newUserEntry(user=newUser2)
        print(databaseManager1.getUserEntry(email="s"))
        print(databaseManager2.getUserEntry(email="s"))
        print(databaseManager1.getAllUserEntryObjects())
    except Exception as e:
        print(e)
