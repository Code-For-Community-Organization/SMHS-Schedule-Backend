import json
from bs4 import BeautifulSoup
from selenium import webdriver
import time


driver = webdriver.Chrome("/Users/jevonmao/Git_directory/Aeries-scraping/chromedriver")
url = "https://my.iusd.org/"
driver.get(url)

username = driver.find_element_by_id("portalAccountUsername")
password = driver.find_element_by_id("portalAccountPassword")

username.send_keys("jevkevceo@gmail.com")
nextItem = driver.find_element_by_id("next")
nextItem.click()
password.send_keys("511969")

driver.find_element_by_id("LoginButton").click()
time.sleep(5)
cookies = driver.get_cookies()


driver.get("https://my.iusd.org/Widgets/ClassSummary/GetClassSummary?IsProfile=True&_=1589939767614")
soup = BeautifulSoup(driver.page_source, "html.parser")
mainJson = soup.find("pre").text

driver.quit()

with open ('data.txt', 'w+') as json_file:
    json.dump(mainJson, json_file)
    newJson = json.load(json_file)


with open ('data.txt', 'r') as json_file:
    file = json.load(json_file)

parsed_json = [{k:v for k,v in classes.items() if k in ['Period', 'RoomNumber', 'TeacherName', 'Percent', 'Average', 'CurrentMark', 'MissingAssignments', 'LastUpdated', 'SchoolName','DistrictName']} for classes in file]


for classes in parsed_json:
    soup = BeautifulSoup(classes["MissingAssignments"],"html.parser")
    misAssignNum = soup.get_text()
    classes["MissingAssignments"] = misAssignNum

print(parsed_json)