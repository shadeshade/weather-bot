import logging
import os

import telebot
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.credentials import TOKEN

load_dotenv(dotenv_path='.env')

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(CUR_DIR)

server = Flask(__name__)

server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\shade\\Desktop\\projects\\weather_bot\\bot.db'
server.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")

db = SQLAlchemy(server)

bot = telebot.TeleBot(TOKEN)

logging.basicConfig(filename=os.path.join(BASE_DIR, 'log.log'), level=logging.DEBUG)
logger = logging.getLogger()
