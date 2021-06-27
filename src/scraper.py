from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from dataclasses import dataclass
from typing import Any
from json.encoder import JSONEncoder
import json
import os

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
    def __init__(self, URL, password, username):
        #Configure website URL and logins
        self.URL = URL
        self.password = password
        self.username = username

        #Set chrome options
        chrome_bin = os.environ.get('GOOGLE_CHROME_BIN')
        chrome_driver_path = os.environ.get('CHROMEDRIVER_PATH')
        options = Options()
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.binary_location = chrome_bin

        

        #Configure webdriver
        self.driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)
        self.driver.get(self.URL)

    def login(self):
        username = self.driver.find_element_by_id("portalAccountUsername")
        username.send_keys(self.username)
        self.driver.find_element_by_id("next").click()
        password = self.driver.find_element_by_id("portalAccountPassword")
        password.send_keys(self.password)
        
        self.driver.find_element_by_id("LoginButton").click()
        try:
            WebDriverWait(self.driver, 8).until(AnyEc(
                EC.presence_of_element_located((By.ID, "AeriesFullPageBody")),
                EC.presence_of_element_located((By.ID, "errorContainer"))
                )
                )
            errorMessageBox = self.driver.find_element_by_id("errorContainer")
            errorMessage: str = errorMessageBox.find_element_by_id("errorMessage").text
            if errorMessageBox is not None:
                if "Too many failed login attempts." in errorMessage:
                    raise FailedAttemptsError("Too many failed login attempts, try again later.")
                elif "The Username and Password entered are incorrect." in errorMessage:
                    raise ValidationError("The Username and Password entered are incorrect.")
                elif "You must enter a password!" in errorMessage:
                    raise EmptyPasswordError("Empty password. You must enter a password.")

        except TimeoutError:
            raise TimeoutError("Unknown error. Timeout waiting for the main grades page to load.")
        except NoSuchElementException:
            pass

    def loadSummary(self):
        self.driver.get("https://aeries.smhs.org/Parent/Widgets/ClassSummary/GetClassSummary?IsProfile=True&_=1622154593572")
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        self.driver.quit()
        return soup.text

    @staticmethod
    def writeFile(filename, JSONFile):
        with open (filename, 'w') as json_file:
            json_file.write(JSONFile)
        

class DataParser:
    
    def __init__(self, rawJSON) -> None:
        self.rawJSON = rawJSON

    def parseData(self) -> list[Period]:
        allClasses: list[Period] = []
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

if __name__ == "__main__":
    requestData: Request = Request("https://aeries.smhs.org/Parent/LoginParent.aspx?page=Dashboard.aspx",
                                        "Mao511969",
                                        "jingwen.mao@smhsstudents.org")
    try:
        requestData.login()
    except Exception as e:
        print(e)

    rawJson = requestData.loadSummary()
    dataParser: DataParser = DataParser(rawJson)
    parsedPeriods: list[Period] = dataParser.parseData()
    encodedPeriods: str = PeriodEncoder().encode(parsedPeriods)