import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.select import Select
import time


class RequestData:
    def __init__(self, URL, password, username):
        self.URL = URL
        self.password = password
        self.username = username
        print(self.username)
        self.driver = webdriver.Chrome("/Users/jevonmao/Git_directory/Scraping_Aeries/ext/chromedriver83")
        self.driver.get(self.URL)
        username = self.driver.find_element_by_id("portalAccountUsername")
        username.send_keys(self.username)
        self.driver.find_element_by_id("next").click()

        password = self.driver.find_element_by_id("portalAccountPassword")
        password.send_keys(self.password)

        self.driver.find_element_by_id("LoginButton").click() 
        self.driver.implicitly_wait(5)

    def LoadSummary(self):
        self.driver.get("https://my.iusd.org/Widgets/ClassSummary/GetClassSummary?IsProfile=True")
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        mainJson = soup.find("pre").text

        self.driver.quit()
        return mainJson

    def LoadDetail(self):
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
        


class ProcessData:
    def __init__(self):
        with open ('data.json','r') as json_file:
            self.file = json.load(json_file)

    def processData(self):
        parsed_json = [{k:v for k,v in classes.items() if k in ["Period", 'RoomNumber','CourseName', 'TeacherName', 'Percent', 'Average', 'CurrentMark', 'MissingAssignments', 'LastUpdated', 'TermGrouping','SchoolName','DistrictName']} for classes in self.file]

        for classes in parsed_json:
            soup = BeautifulSoup(classes["MissingAssignments"],"html.parser")
            misAssignNum = soup.get_text()
            classes["MissingAssignments"] = misAssignNum
        return parsed_json


# RequestData = RequestData("https://my.iusd.org/LoginParent.aspx",511969,"jevkevceo@gmail.com")
# mainJson = RequestData.LoadSummary()
# RequestData.writeFile("data.json",mainJson)
ProcessData = ProcessData()
with open('parsedSummary.json','w') as json_file:
    processedData = str(ProcessData.processData()).replace("\'", "\"")
    json_file.write(processedData)
# RequestData.LoadDetail()

