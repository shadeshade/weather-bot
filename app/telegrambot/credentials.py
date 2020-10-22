import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
HEROKU_DEPLOY_DOMAIN = os.getenv("HEROKU_DEPLOY_DOMAIN")
NGROK_DEPLOY_DOMAIN = os.getenv("NGROK_DEPLOY_DOMAIN")

DEBUG = os.getenv("DEBUG")
SERVER_IP = os.getenv("SERVER_IP")
PORT = os.getenv("PORT")