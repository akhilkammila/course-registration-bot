# sample run command: python3 main.py 21362

from urllib.request import urlopen
import time
from bs4 import BeautifulSoup
from twilio.rest import Client
import requests
from pushovercreds import APItoken, USERkey

class RegistrationBot:
  """
  Gets classes to register from file
  Sets up important vars
  """
  def __init__(self):
    with open("classes.txt", "r") as f:
      self.classes = [line.rstrip() for line in f.readlines()]
    self.previous_state = [0] * (len(self.classes))

    self.url = "https://api.pushover.net/1/messages.json"
  
  """
  Sends a simple message with the classes being tracked
  Used to check that program is still running
  """
  def statusCheck(self):
    params = {
      "token": APItoken,
      "user": USERkey,
      "message": f"{self.classes}",
      "title": f"Status Check: We are currently tracking these classes",
      "priority": 0  # Set the priority level (0 for normal)
    }
    response = requests.post(self.url, data=params)

  """
  Helper method that gets the registration info for a class given its url
  """
  def getClassStatus(self, url):
    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")
    
    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text
  
  """
  Loops through every class, and checks its availability
  Sends a pushover notification if the availability has changed
    sends if it changed from closed --> open or open --> closed
    on the first request, sends it only if it changed from closed --> open
  """
  def checkAllClasses(self):
    for index, arg in enumerate(self.classes):
      # gatech's course info url
      req = self.getClassStatus(f"https://registration.banner.gatech.edu/StudentRegistrationSsb/ssb/searchResults/getEnrollmentInfo?term=202308&courseReferenceNumber={arg}")

      # retrieve relevant data
      enrollment_available = int(req.split("\n")[2].split(" ")[-1])
      waitlist_actual = int(req.split("\n")[4].split(" ")[-1])
      open = enrollment_available > waitlist_actual

      # send pushover req
      if open != self.previous_state[index]:
        self.previous_state[index] = open

        openString = "Open" if open else "Closed"
        params = {
            "token": APItoken,
            "user": USERkey,
            "message": f"{arg}\n{req}",
            "title": f"{arg} is {openString}",
            "priority": 0  # Set the priority level (0 for normal)
        }

        response = requests.post(self.url, data=params)
  
  """
  Continuous loop to check classes every x seconds
  Params:
    checks every x seconds
    sends uptime notification every y checks (aka every x*y seconds)
  """
  def runContinuously(self, checkSeconds, uptimeMultiplier):
    while True:
      self.statusCheck()
      for i in range(uptimeMultiplier):
        self.checkAllClasses()
        time.sleep(checkSeconds)

if __name__ == "__main__":
  mybot = RegistrationBot()
  mybot.runContinuously(3,1200)