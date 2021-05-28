from flask import Flask, render_template, url_for, abort, Response, request
import json
import os
import json
from json.encoder import JSONEncoder
from urllib import parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.select import Select
import time
from dataclasses import dataclass
import typing
from typing import Any

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

class Request:
    def __init__(self, URL, password, username):
        self.URL = URL
        self.password = password
        self.username = username
        self.driver = webdriver.Chrome("D:/Programming/Scraping_Aeries/ext/chromedriver.exe")
        self.driver.get(self.URL)
        username = self.driver.find_element_by_id("portalAccountUsername")
        username.send_keys(self.username)
        self.driver.find_element_by_id("next").click()

        password = self.driver.find_element_by_id("portalAccountPassword")
        password.send_keys(self.password)

        self.driver.find_element_by_id("LoginButton").click() 
        self.driver.implicitly_wait(5)

    def loadSummary(self):
        self.driver.get("https://aeries.smhs.org/Parent/Widgets/ClassSummary/GetClassSummary?IsProfile=True&_=1622154593572")
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        self.driver.quit()
        return soup.text

    def loadDetail(self):
        self.driver.get("https://my.iusd.org/GradebookDetails.aspx")

        selectBox = self.driver.find_element_by_id('ctl00_MainContent_subGBS_dlGN')
        options = [option.get_attribute("value") for option in selectBox.find_elements_by_tag_name("option")]
        for value in options:
            selector = Select(self.driver.find_element_by_id('ctl00_MainContent_subGBS_dlGN'))
            selector.select_by_value(value)
            time.sleep(3)

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            assignmentDiv = soup.find("div", class_="AllAssignments")
            assignmentBody = assignmentDiv.find("table").find("tbody")
            assignment = assignmentBody.findAll("tr",recursive=False)
       
            for a in assignment:
                
                assignmentTitle = a.find(class_="TextHeading")
                assignmentDes = a.find(class_="TextSubSectionCategory")
                assignmentDetail = a.findAll(class_="InlineData")
                if assignmentTitle and assignmentDes and assignmentDetail != []:
                    print(assignmentTitle.text,assignmentDes.text,[detailText.text for detailText in assignmentDetail])
        self.driver.quit()


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


app = Flask(__name__)

app.config['DEBUG'] = True

@app.route('/api/v1/grades/', methods=['GET'])
def home():
    if 'email' in request.args and 'password' in request.args:
        email: str = request.args['email']
        password: str = request.args['password']
        requestData: Request = Request("https://aeries.smhs.org/Parent/LoginParent.aspx?page=Dashboard.aspx",
                                       password,
                                       email)
        rawJson = requestData.loadSummary()
        dataParser: DataParser = DataParser(rawJson)
        parsedPeriods: list[Period] = dataParser.parseData()
        encodedPeriods: str = PeriodEncoder().encode(parsedPeriods)
        return encodedPeriods
    else:
        abort(Response("Error: NO email and password provided. Please provide a valid email and password login."))

if __name__ == "__main__":
    app.run()