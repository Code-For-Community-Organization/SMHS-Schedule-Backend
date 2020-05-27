import json
from bs4 import BeautifulSoup


with open ('data.txt', 'r') as json_file:
    file = json.load(json_file)



# driver.get("https://my.iusd.org/Transcripts.aspx")
# gDetailTable = driver.find_elements_by_xpath("//*[@id='ctl00_MainContent_subHIS_Histories_UpdatePanel']/table/tbody/tr/td[1]/table")

# html = gDetailTable[0].get_attribute('innerHTML')
# soup = BeautifulSoup(html,"html.parser")
# table_row = soup.find_all("tr",id = re.compile(r'.*_ReadRow\d+'))
driver.get("https://my.iusd.org/Widgets/ClassSummary/GetClassSummary?IsProfile=True&_=1589939767614")
soup = BeautifulSoup(driver.page_source, "html.parser")
mainJson = soup.find("pre").text

driver.quit()
with open ('data.txt', 'w+') as json_file:
    json.dump(mainJson, json_file)
    newJson = json.load(json_file)




parsed_json = [{k:v for k,v in classes.items() if k in ['Period', 'RoomNumber', 'TeacherName', 'Percent', 'Average', 'CurrentMark', 'MissingAssignments', 'LastUpdated', 'SchoolName','DistrictName']} for classes in file]


for classes in parsed_json:
    soup = BeautifulSoup(classes["MissingAssignments"],"html.parser")
    misAssignNum = soup.get_text()
    classes["MissingAssignments"] = misAssignNum

print(parsed_json)