import logging
import os

import telebot
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from weather_app.credentials import TOKEN

load_dotenv(dotenv_path='.env')

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(CUR_DIR)

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")

db = SQLAlchemy(app)

bot = telebot.TeleBot(TOKEN)

logging.basicConfig(filename=os.path.join(BASE_DIR, 'log.log'), level=logging.DEBUG)
logger = logging.getLogger()
