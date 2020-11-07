import logging
import os

import telebot
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.credentials import TOKEN

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(CUR_DIR)

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
path_to_db = os.path.join(BASE_DIR, 'bot.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{path_to_db}'

db = SQLAlchemy(app)

bot = telebot.TeleBot(TOKEN)

logging.basicConfig(filename=os.path.join(BASE_DIR, 'log.log'), level=logging.DEBUG)
logger = logging.getLogger()

# handler = logging.FileHandler(os.path.join(BASE_DIR, 'log.log'), 'w', encoding='utf8')
# logger = logging.getLogger()
# logger.addHandler(handler)
# logger.setLevel(logging.DEBUG)
