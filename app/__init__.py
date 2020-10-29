import os

import telebot
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.telegrambot.credentials import TOKEN

app = Flask(__name__)

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(CUR_DIR)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
path_to_db = os.path.join(BASE_DIR, 'bot.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{path_to_db}'
db = SQLAlchemy(app)
bot = telebot.TeleBot(TOKEN)
