"""
Goal: get a list of possible classes to choose from

Can we do this using course critique API?
Look into GT scheduler

GT scheduler gets json using web crawler, periodically updated thru github actions
    1) run own web crawler
    2) just use gt scheduler's link

api = "https://gt-scheduler.github.io/crawler-v2/202402.json"

For MVP: Users put in a CRN on their own?
"""

import requests
import json

url = "https://gt-scheduler.github.io/crawler-v2/202402.json"

response = requests.get(url)
data = response.json()

with open('gtClasses.txt', 'w') as outfile:
    json.dump(data, outfile)