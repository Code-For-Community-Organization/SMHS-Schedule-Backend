from cryptography.fernet import Fernet
import json

with open("database.json", "r+") as db:
    key = Fernet.generate_key()
    cipherSuite = Fernet(key)
    cipherText = cipherSuite.encrypt(b"Mao511969")

    dataBaseDict = {'Password':cipherText.decode("utf-8")}
    json.dump(dataBaseDict, db)

with open("database.json", "r") as db:
    passwordContent = json.load(db)
    hash = str.encode(passwordContent["Password"])
    print(cipherSuite.decrypt(hash))
