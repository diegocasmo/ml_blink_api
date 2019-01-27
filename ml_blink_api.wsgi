#!/usr/bin/python
# Load environmental variables
from dotenv import load_dotenv
load_dotenv(dotenv_path='/var/www/ml_blink_api/.env')

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,'/var/www/ml_blink_api/')

from ml_blink_api import app as application
