import telebot
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.telegrambot.credentials import TOKEN

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot.db'
db = SQLAlchemy(app)
bot = telebot.TeleBot(TOKEN)

# from app import main