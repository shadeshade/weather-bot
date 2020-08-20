from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import telebot

from telegrambot.credentials import *
from telegrambot.mastermind import *
from telegrambot.settings import *

# from telegrambot.models import User
bot = telebot.TeleBot(TOKEN)

server = Flask(__name__)
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot.db'
scheduler = BackgroundScheduler()
db = SQLAlchemy(server)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    chat_id = db.Column(db.Integer, unique=True, nullable=False)
    city_name = db.Column(db.String(20), )
    city_name2 = db.Column(db.String(20), )
    city_name3 = db.Column(db.String(20), )

    def __repr__(self):
        return f"User('{self.username}', '{self.chat_id}', '{self.city_name}', '{self.city_name2}', '{self.city_name3}')"


@server.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    # bot.remove_webhook()
    # sleep(1)
    if DEBUG:
        s = bot.set_webhook(f'{NGROK_DEPLOY_DOMAIN}/{TOKEN}')
    else:
        s = bot.set_webhook(f'{HEROKU_DEPLOY_DOMAIN}/{TOKEN}')

    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


set_webhook()


@server.route(f'/{TOKEN}', methods=['POST'])
def get_update():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "", 200


# Handle '/start'
@bot.message_handler(commands=['start'])
def command_start(message, ):
    response = get_start(message.from_user.first_name)
    return bot.send_message(message.chat.id, text=response, )


# Handle '/help'
@bot.message_handler(commands=['help'])
def command_help(message, ):
    response = get_help()
    return bot.send_message(message.chat.id, text=response, )


# Handle '/daily'
@bot.message_handler(commands=['daily'])
def command_daily(message):
    if not bool(User.query.filter_by(chat_id=message.chat.id).first()):
        new_user = User(username=message.from_user.first_name, chat_id=message.chat.id, city_name='маха')
        db.session.add(new_user)
        db.session.commit()
    set_daily(message.chat.id)
    response = 'Schedule was set up'
    return bot.send_message(message.chat.id, text=response, )


# Handle '/daily' (setting a daily reminder)
def set_daily(chat_id):
    try:
        scheduler.remove_all_jobs()
        scheduler.add_job(daily_info, trigger='interval', seconds=5, args=[chat_id])
        scheduler.start()
    except:
        pass


# Handle '/daily' (sending a reminder)
def daily_info(chat_id):
    user = User.query.filter_by(chat_id=chat_id).first()
    city_name = user.city_name
    response = get_daily(city_name)
    return bot.send_message(chat_id, text=response, )


# @app.route(f'/{TOKEN}', methods=['POST'])
# def respond():
#     update = request.get_json()
#     # Telegram understands UTF-8, so encode text for unicode compatibility
#     text = update.message.text.encode('utf-8').decode()
#     print("got text message :", text)
#
#     chat_id = update.message.chat.id
#     msg_id = update.message.message_id
#
#     global _chat_id
#     _chat_id = chat_id
#
#     username = update.message.chat.first_name
#
#     # if transliterate_name(text):
#     #     city_name = transliterate_name(text)
#
#     if not bool(User.query.filter_by(chat_id=chat_id).first()):
#         new_user = User(username=username, chat_id=chat_id, city_name='маха')
#         db.session.add(new_user)
#         db.session.commit()
#
#     if text == '/start':
#         # username = update.message.chat.first_name
#         start(update, username)
#         return 'ok'
#         # response = start_command(username)
#     elif text == '/help':
#         response = help_command()
#     elif text == '/daily':
#         response = 'Schedule was set up'
#         daily()
#     else:
#         response = get_response(text)
#
#     bot.send_message(chat_id=chat_id, text=response, )
#     return 'ok', 200


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def respond(message):
    response = get_response(message.text)
    bot.send_message(chat_id=message.chat.id, text=response, )
    return 'ok', 200


if __name__ == '__main__':
    server.run(threaded=True, host=SERVER_IP, port=PORT, debug=DEBUG)
