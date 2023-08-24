from pushovercreds import APItoken
from pushovercreds import USERkey
import requests

url = "https://api.pushover.net/1/messages.json"

params = {
    "token": APItoken,
    "user": USERkey,
    "message": "Hello from Pushover!",
    "title": "Notification Title",
    "priority": 0  # Set the priority level (0 for normal)
}

response = requests.post(url, data=params)