"""
View some stats about class data
Class data json should be saved to gtClasses.txt before running
"""

"""
Structure:
courses:
    course name: list
        0 --> course full name
        1 --> class section dictionary
        class section Code: list
            0 --> CRN
            1 --> list of more data
        2 --> empty list?
        3 --> description
"""

import requests
import json

url = "https://gt-scheduler.github.io/crawler-v2/202402.json"

response = requests.get(url)
data = response.json()

courses = data["courses"]
crns = []

# Store data
courseList = [course for course in courses] # just a list of course names

# Analyze data

for className, classData in courses.items():
    for sectionCode in classData[1].keys():
        crn = classData[1][sectionCode][0]
        crns.append((crn, className, sectionCode))

print(courseList[0])
print(crns[0])

print(len(courseList))
print(len(crns))