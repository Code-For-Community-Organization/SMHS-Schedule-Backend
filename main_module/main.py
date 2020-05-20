import json


with open ('data.txt', 'r') as json_file:
    file = json.load(json_file)


# aaa = """Period: {period}, Room: {room}, Teacher: {teacher}, Grade: {grade}, 
#           Last updated: {update}""".format(period = file[0]['Period'], 
#           room = file[0]["RoomNumber"], teacher = file[0]["TeacherName"],
#           grade = file[0]["CurrentMarkAndScore"], update=file[0]['LastUpdated']

parsed_json = [{k:v for k,v in classes.items() if k in ['Period', 'RoomNumber', 'TeacherName', 'CurrentMarkandScore', 'LastUpdated']} for classes in file]

print(parsed_json)