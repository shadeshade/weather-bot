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

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")

# path_to_db = os.path.join(BASE_DIR, 'bot.db')
# app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{path_to_db}'
# a = f'sqlite:///{path_to_db}'
# b = os.path.dirname(os.getenv("SQLALCHEMY_DATABASE_URI"))


db = SQLAlchemy(app)

bot = telebot.TeleBot(TOKEN)

logging.basicConfig(filename=os.path.join(BASE_DIR, 'log.log'), level=logging.DEBUG)
logger = logging.getLogger()


def create_app(config_file='settings.py'):
    from app.commands import create_tables

    _app = app
    app.cli.add_command(create_tables)

    return _app
