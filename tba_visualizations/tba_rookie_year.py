from os import environ

import requests
from dotenv import load_dotenv

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/event/2022hop/matches"
TBA_API_KEY = environ["TBA_API_KEY"]
