import json
from bs4 import BeautifulSoup


with open ('data.txt', 'r') as json_file:
    file = json.load(json_file)



parsed_json = [{k:v for k,v in classes.items() if k in ['Period', 'RoomNumber', 'TeacherName', 'Percent', 'Average', 'CurrentMark', 'MissingAssignments', 'LastUpdated', 'SchoolName','DistrictName']} for classes in file]


for classes in parsed_json:
    soup = BeautifulSoup(classes["MissingAssignments"],"html.parser")
    misAssignNum = soup.get_text()
    classes["MissingAssignments"] = misAssignNum

print(parsed_json)