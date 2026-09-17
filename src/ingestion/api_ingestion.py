import json
import logging
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

API_URL = os.getenv("API_URL")
RAW_DATA_PATH = Path("data/raw/posts.json")