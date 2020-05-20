from bs4 import BeautifulSoup
from selenium import webdriver
import time
import json
import re




driver = webdriver.Chrome("/Users/jevonmao/Git_directory/Scraping_Aeries/ext/chromedriver83")
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
gHomeTable = driver.find_element_by_class_name("classSummaryTable")
html = gHomeTable.get_attribute('innerHTML')


soup = BeautifulSoup(html, "html.parser")

table_body = soup.find_all(attrs={"data-uid":True})

for cell in table_body:
    className = cell.find(class_="tinymodeTC")
    info = cell.find(class_="tinymodeTC").text
   
    teacherName = re.search("[A-Za-z]+, *[A-Z]", info).group()

    index = info.index(teacherName)
    className = info[:index]
    updateDate = re.search("[a-z A-Z]* [0-9]{2}",info)
    print(teacherName, className)

driver.get("https://my.iusd.org/Transcripts.aspx")
gDetailTable = driver.find_elements_by_xpath("//*[@id='ctl00_MainContent_subHIS_Histories_UpdatePanel']/table/tbody/tr/td[1]/table")

html = gDetailTable[0].get_attribute('innerHTML')
soup = BeautifulSoup(html,"html.parser")
table_row = soup.find_all("tr",id = re.compile(r'.*_ReadRow\d+'))
print(table_row[0])
driver.quit()
#grade = [cell.find(class_="MarkandGrade").text for cell in table_body]


