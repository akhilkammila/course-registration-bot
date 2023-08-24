# sample run command: python3 main.py 21362

from urllib.request import urlopen
import time
from bs4 import BeautifulSoup
from twilio.rest import Client
from creds import TWILIO_NUMBER, TARGET_NUMBER, ACCOUNT_SID, AUTH_TOKEN

account_sid = ACCOUNT_SID
auth_token = AUTH_TOKEN
twilio_number = TWILIO_NUMBER
target_number = TARGET_NUMBER

def process(url):
  html = urlopen(url).read()
  soup = BeautifulSoup(html, features="html.parser")

  # kill all script and style elements
  # for script in soup(["script", "style"]):
  #     script.extract()    # rip it out
  
  # get text
  text = soup.get_text()

  # break into lines and remove leading and trailing space on each
  lines = (line.strip() for line in text.splitlines())
  # break multi-headlines into a line each
  chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
  # drop blank lines
  text = '\n'.join(chunk for chunk in chunks if chunk)
  
  return text

print("starting program")
# 1. Get the classes to track
classes = None
with open("classes.txt", "r") as f:
  classes = [line.rstrip() for line in f.readlines()]

# 2. Twilio working check
print("classes loaded")
client = Client(account_sid, auth_token)
message = client.messages.create(
                                  body=f"{classes}",
                                  from_=f'{twilio_number}',
                                  to=f'{target_number}'
                                )

# 2. Continuously check for class availability
previous_state = [0] * (len(classes))
while True:
  for index, arg in enumerate(classes):
    # gatech's course info url
    req = process(f"https://registration.banner.gatech.edu/StudentRegistrationSsb/ssb/searchResults/getEnrollmentInfo?term=202308&courseReferenceNumber={arg}")

    # retrieve relevant data
    enrollment_available = int(req.split("\n")[2].split(" ")[-1])
    waitlist_actual = int(req.split("\n")[4].split(" ")[-1])
    open = enrollment_available > waitlist_actual

    # call twilio
    if open != previous_state[index]:
      previous_state[index] = open
      
      client = Client(account_sid, auth_token)
      message = client.messages.create(
                                  body=f"{arg}\n{req}",
                                  from_=f'{twilio_number}',
                                  to=f'{target_number}'
                                )
    
  time.sleep(3)