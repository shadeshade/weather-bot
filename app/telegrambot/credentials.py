import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
BOT_NAME = os.getenv("BOT_NAME")
HEROKU_DEPLOY_DOMAIN = os.getenv("HEROKU_DEPLOY_DOMAIN")
NGROK_DEPLOY_DOMAIN = os.getenv("NGROK_DEPLOY_DOMAIN")
