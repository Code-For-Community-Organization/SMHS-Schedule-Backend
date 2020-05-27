import json
from bs4 import BeautifulSoup
from selenium import webdriver


class RequestData:
    def __init__(self, URL, password, username):
        self.URL = URL
        self.password = password
        self.username = username

        self.driver = webdriver.Chrome("/Users/jevonmao/Git_directory/Scraping_Aeries/ext/chromedriver83")
        self.driver.get(self.URL)
        username = self.driver.find_element_by_id("portalAccountUsername")
        password = self.driver.find_element_by_id("portalAccountPassword")

        username.send_keys("jevkevceo@gmail.com")
        password.send_keys("511969")

        self.driver.find_element_by_id("next").click()
        self.driver.find_element_by_id("next").click() 
        self.driver.implicitly_wait(5)

    def LoadJson(self):
        self.driver.get("https://my.iusd.org/Widgets/ClassSummary/GetClassSummary?IsProfile=True")
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        mainJson = soup.find("pre").text

        self.driver.quit()
        return mainJson

    @staticmethod
    def writeFile(filename, JSONFile):
        with open (filename, 'w') as json_file:
            json_file.write(JSONFile)
        


class ProcessData:
    def __init__(self):
        with open ('data.txt','r') as json_file:
            self.file = json.load(json_file)

    def processData(self):
        parsed_json = [{k:v for k,v in classes.items() if k in ['Period', 'RoomNumber', 'TeacherName', 'Percent', 'Average', 'CurrentMark', 'MissingAssignments', 'LastUpdated', 'SchoolName','DistrictName']} for classes in self.file]

        for classes in parsed_json:
            soup = BeautifulSoup(classes["MissingAssignments"],"html.parser")
            misAssignNum = soup.get_text()
            classes["MissingAssignments"] = misAssignNum
        return parsed_json


RequestData = RequestData("https://my.iusd.org/LoginParent.aspx",511969,"jevkevceo@gmail.com")
ProcessData = ProcessData()


