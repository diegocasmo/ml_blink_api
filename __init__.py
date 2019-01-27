from dotenv import load_dotenv
load_dotenv() # Load environmental variables

from ml_blink_api import app

if __name__ == '__main__':
  app.run()
