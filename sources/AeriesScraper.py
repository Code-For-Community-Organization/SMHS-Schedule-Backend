from json.encoder import JSONEncoder
from dataclasses import dataclass
import requests
import json
from typing import List
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

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
            'portalAccountUsername': self.username,
            'portalAccountPassword': self.password}

        #Setup retry mechanism with total 5 retries, backoff by increasing number of seconds
        #Retry on connectivity issues and HTTPS status codes given
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])

        #Create a request session (with to automatically close)
        self.session = requests.Session()

        #Configure the session retry with matching http pattern, using http adaptor
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        try:
            post = self.session.post(self.loginURL, data=payload)
        except requests.exceptions.RequestException as err:
            # catastrophic error. bail.
            raise SystemExit(err)
        except requests.exceptions.HTTPError as err:
            # Some 4xx http error. bail.
            raise SystemExit(err)

    def fetchSummary(self) -> str:
        #JSON grades URL to fetch
        contentURL: str = 'https://aeries.smhs.org/Parent/Widgets/ClassSummary/GetClassSummary?IsProfile=True'

        #If the request session is not None (login has been called)
        if self.session is not None:

            #Send a GET request on grades summary JSON url
            content = self.session.get(contentURL)

            #Handle any possible errors
            try:
                #No redirect likely means successful, redirect means failed login
                if not content.history:
                    #Forgiveness not permission, test if valid JSON
                    json.loads(content.text)
                    return content.text
                else:
                    #If redirected to login page, probably invalid username or password
                    raise ValidationError("Invalid username or password")

            #Handle invalid JSON error
            except ValueError as err:
                raise ValidationError(err)

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

    email: str = input("Enter your email or username: ")
    password: str = input("Enter your password: ")
    startTime = time.time()

    try:
        requestData: Request = Request(password,
                                email)
        requestData.login()
        rawJson = requestData.fetchSummary()
        dataParser: DataParser = DataParser(rawJson)
        parsedPeriods: List[Period] = dataParser.parseData()
        encodedPeriods: str = PeriodEncoder().encode(parsedPeriods)
        DataParser.writeFile('class-summary.json', JSONFile=encodedPeriods)
    except Exception as e:
        print(e)
    
    print(f"----- {time.time() - startTime} seconds elapsed -----")