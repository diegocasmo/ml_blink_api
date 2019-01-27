# Load environmental variables
from dotenv import load_dotenv
load_dotenv()

# Load application
from ml_blink_api import app
if __name__ == '__main__':
  app.run()
