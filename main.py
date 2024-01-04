# sample run command: python3 main.py 21362

import time
import requests
import re
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
from postmarkcreds import api_key

apiBaseUrl = os.getenv('apiBaseUrl')
if not apiBaseUrl: apiBaseUrl = 'http://127.0.0.1:5000'

def send_email(email, title, body):
  postmark_token = api_key
  sender_email = 'notifier@gtregistration.com'
  subject = f'[GT Registration] {title}'
  text_body = f'{body}'

  headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'X-Postmark-Server-Token': postmark_token
  }
  payload = {
      'From': sender_email,
      'To': email,
      'Subject': subject,
      'TextBody': text_body,
      'MessageStream': 'outbound'
  }
  response = requests.post('https://api.postmarkapp.com/email', headers=headers, data=json.dumps(payload))
  return response

def statusToText(status):
  if status == 0: return "Accurate class data unavailable"
  if status == 1: return "Open"
  if status == 2: return "Waitlist Open"
  if status == 3: return "Waitlist Closed"
  if status == 4: return "Class does not exist"
  return "Error"


"""
Gets the status of a given class given crn
Statuses
  0: undefined (unchecked, or negatives error)
  1: open
  2: closed, waitlist open
  3: closed, waitlist closed
  4: not a class
"""
def getClassStatus(crn):
  # get proper url
  month = datetime.now().month
  year = datetime.now().year
  if month > 8:
    month = 2
    year += 1
  elif 3 <= month <= 8: month = 8
  elif month <= 2: month = 2
  yearstring = f"{year:04}{month:02}"
  
  url = f"https://registration.banner.gatech.edu/StudentRegistrationSsb/ssb/searchResults/getEnrollmentInfo?term={yearstring}&courseReferenceNumber={crn}"

  html = requests.get(url, verify=False).content
  soup = BeautifulSoup(html, features="html.parser")
  
  # get six vals: enrollment actual, maximum, seats available, waitlist capacity, actual, seats available
  text = soup.get_text()
  pattern = r":\s*(\d+)"
  numbers = re.findall(pattern, text)
  numbers = [int(num) for num in numbers]

  # get status code
  if len(numbers) != 6: return 4 # invalid class

  enr_actual, enr_max, enr_avail, waitlist_max, waitlist_actual, waitlist_avail = numbers

  if enr_avail < 0 or waitlist_actual < 0: return 0 # weird conditions: return undefined
  if enr_avail > waitlist_actual: return 1 # open
  else:
    if waitlist_avail > 0: return 2
    else: return 3

"""
From backend, gets a list of
user email -->
  first_time: bool
  courses -->
    crn: integer
    note: string
    status: integer
  
If first time: sends email with status of every class
Otherwise: sends separate email for each class, only if status changed

After going through all users, notify backend of any class status changes
"""
def checkClasses():
  # Request data from backend
  geturl = f"{apiBaseUrl}/get_user_classes"
  posturl = f"{apiBaseUrl}/update_class_statuses"

  response = requests.get(geturl)
  if response.status_code != 200: return
  data = response.json()

  # Check courses
  changedStatus = {} # to send updates to server, only if status changed

  for email in data.keys():
    currStatuses = {}
    first = data[email]['first_time']

    # Add courses to currStatuses
    for courseData in data[email]['courses']:
      crn = courseData['crn']

      # Find status, update statuses
      if crn in changedStatus: newStatus = changedStatus[crn]
      else: newStatus = getClassStatus(courseData['crn'])

      # Update email data
      if first: currStatuses[crn] = newStatus # first --> just the status
      elif newStatus != courseData['status']: currStatuses[crn] = (newStatus, courseData['note']) # otherwise --> (status, note)

      if newStatus != courseData['status']: changedStatus[crn] = newStatus
    
    # Send out emails
    if first:
      title = "Classlist Updated"
      preppedVals = [(crn, statusToText(status)) for crn, status in currStatuses.items()]
      body = "\n".join([f'{crn}: {text}' for crn, text in preppedVals])
      send_email(email, title, body)
    else:
      for crn, pair in currStatuses.items():
        statusText = statusToText(pair[0])
        title = f"{crn} is {statusText}"
        body = f"Note: {pair[1]}" if pair[1] else ""
        send_email(email, title, body)
  
  # Update server's courses
  if len(changedStatus) > 0: response = requests.post(posturl, json=changedStatus)

"""
Continuous loop to run function every x seconds
"""
def runContinuously(function, interval):
  while True:
    start = time.time()
    function()
    end = time.time()

    elapsed = end - start
    wait = interval - elapsed
    if wait > 0: time.sleep(wait)

if __name__ == "__main__":
  runContinuously(checkClasses, 10)