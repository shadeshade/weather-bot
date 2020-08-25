import telebot
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.telegrambot.credentials import TOKEN


server = Flask(__name__)

server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot.db'
db = SQLAlchemy(server)
bot = telebot.TeleBot(TOKEN)

from app import main
