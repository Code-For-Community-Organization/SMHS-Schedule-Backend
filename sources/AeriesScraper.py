from json.encoder import JSONEncoder
from dataclasses import dataclass
import requests
import json
from typing import List
import time

@dataclass
class Period():
    periodNum: int
    periodName: str
    teacherName: str
    gradePercent: float
    currentMark: str
    isPrior: bool

class PeriodEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
class FailedAttemptsError(Exception):
    pass

class ValidationError(Exception):
    pass

class EmptyPasswordError(Exception):
    pass

#https://stackoverflow.com/questions/16462177/selenium-expected-conditions-possible-to-use-or
class AnyEc:
    """ Use with WebDriverWait to combine expected_conditions
        in an OR.
    """
    def __init__(self, *args):
        self.ecs = args
    def __call__(self, driver):
        for fn in self.ecs:
            try:
                if fn(driver): return True
            except:
                pass

class Request:
    def __init__(self, password: str, username: str):
        #URL the login form points to, we POST this URL
        self.loginURL: str = 'https://aeries.smhs.org/Parent/LoginParent.aspx'
        self.password: str = password
        self.username: str = username
        self.session: requests.sessions.Session = None

    def login(self):
        #Login information to be sent as payload
        payload: dict[str, str] = {
            'portalAccountUsername': 'jingwen.mao@smhsstudents.org',
            'portalAccountPassword': 'Mao511969'}
    
        #Create a request session (with to automatically close)
        with requests.Session() as session:
            post = session.post(self.loginURL, data=payload)
            self.session: requests.sessions.Session = session

    def fetchSummary(self) -> str:
        #JSON grades URL to fetch
        contentURL: str = 'https://aeries.smhs.org/Parent/Widgets/ClassSummary/GetClassSummary?IsProfile=True'

        #If the request session is not None (login has been called)
        if self.session is not None:
            #Get JSON raw text and return it
            content = self.session.get(contentURL)
            return content.text
        
class DataParser:
    
    def __init__(self, rawJSON) -> None:
        self.rawJSON = rawJSON

    def parseData(self) -> List[Period]:
        allClasses: List[Period] = []
        for period in json.loads(self.rawJSON):
            semesterTime: bool = period['TermGrouping'] == 'Prior Terms'
            currentPeriod: Period = Period(periodNum=period["Period"],
                                    periodName=period["CourseName"],
                                    teacherName=period["TeacherName"],
                                    gradePercent=period["Percent"],
                                    currentMark=period["CurrentMark"],
                                    isPrior=semesterTime)
            allClasses.append(currentPeriod)
        return allClasses

    @staticmethod
    def writeFile(filename, JSONFile):
        with open (filename, 'w') as json_file:
            json_file.write(JSONFile)

if __name__ == "__main__":
    startTime = time.time()

    email: str = input("Enter your email or username: ")
    password: str = input("Enter your password: ")

    requestData: Request = Request(password,
                                   email)
    try:
        requestData.login()
    except Exception as e:
        print(e)

    rawJson = requestData.fetchSummary()
    dataParser: DataParser = DataParser(rawJson)
    parsedPeriods: List[Period] = dataParser.parseData()
    encodedPeriods: str = PeriodEncoder().encode(parsedPeriods)
    DataParser.writeFile('class-summary.json', JSONFile=encodedPeriods)

    print(f"----- {time.time() - startTime} seconds elapsed -----")