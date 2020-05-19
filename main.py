from bs4 import BeautifulSoup
from selenium import webdriver
import time
import json
import re




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
table = driver.find_element_by_class_name("classSummaryTable")
html = table.get_attribute('innerHTML')


soup = BeautifulSoup(html, "html.parser")

table_body = soup.find_all(attrs={"data-uid":True})

for cell in table_body:
    className = cell.find(class_="tinymodeTC")
    print(cell.text)  
    info = cell.find(class_="tinymodeTC").text
    
    for word in info:
        teacherName = re.findall("[A-Za-z]+, *[A-Z]", word)
        index = word.index("Teacher")
        print(word[:index])


#grade = [cell.find(class_="MarkandGrade").text for cell in table_body]


