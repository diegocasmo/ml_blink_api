# Load environmental variables
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path="%s/.env" % os.getcwd())

# Load application
from ml_blink_api import app
if __name__ == '__main__':
  app.run()
