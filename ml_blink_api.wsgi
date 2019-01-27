#!/usr/bin/python
# Load environmental variables
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path="%s/.env" % os.getcwd())

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/ml_blink_api/")

from ml_blink_api import app as application
