import json

count = 0
c=0
with open('employee_data.txt', 'r') as outfile:
    employees=json.load(outfile)
print(employees["00002"])