import telegram
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

from telebot.credentials import *
from telebot.mastermind import *
from telebot.settings import *

# from telebot.models import User

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot.db'
scheduler = BackgroundScheduler()
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    chat_id = db.Column(db.Integer, unique=True, nullable=False)
    city_name = db.Column(db.String(20), )
    city_name2 = db.Column(db.String(20), )
    city_name3 = db.Column(db.String(20), )

    def __repr__(self):
        return f"User('{self.username}', '{self.chat_id}', '{self.city_name}', '{self.city_name2}', '{self.city_name3}',)"


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    if DEBUG:
        s = bot.setWebhook(f'{NGROK_DEPLOY_DOMAIN}/{TOKEN}')
    else:
        s = bot.setWebhook(f'{HEROKU_DEPLOY_DOMAIN}/{TOKEN}')

    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


set_webhook()


@app.route(f'/{TOKEN}', methods=['POST'])
def respond():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode('utf-8').decode()
    print("got text message :", text)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    global _chat_id
    _chat_id = chat_id

    username = update.message.chat.first_name

    # if transliterate_name(text):
    #     city_name = transliterate_name(text)

    if not bool(User.query.filter_by(chat_id=_chat_id).first()):
        new_user = User(username=username, chat_id=_chat_id, city_name='маха')
        db.session.add(new_user)
        db.session.commit()

    if text == '/start':
        # username = update.message.chat.first_name
        response = start_command(username)
    elif text == '/help':
        response = help_command()
    elif text == '/daily':
        response = 'Schedule was set up'
        daily()
    else:
        response = get_response(text)

    bot.sendMessage(chat_id=chat_id, text=response, )
    return 'ok'


def daily():
    try:
        scheduler.remove_all_jobs()
        scheduler.add_job(daily_info, trigger='interval', seconds=5, )
        scheduler.start()
    except:
        pass


def daily_info():
    user = User.query.filter_by(chat_id=_chat_id).first()
    city_name = user.city_name
    chat_id = user.chat_id
    response = daily_command(city_name)
    return bot.sendMessage(chat_id, text=response, )


#
# def daily():
#     # bot.sendMessage(chat_id=chat_id, text='text_')
#     schedule.every(3).seconds.do(daily_info)
#     # schedule.every().day.at().do(daily_info)
#     Thread(target=schedule_checker).start()
#     # schedule_checker()
#
#
# def schedule_checker():
#     while True:
#         sleep(1)
#         schedule.run_pending()


if __name__ == '__main__':
    app.run(threaded=True, host=SERVER_IP, port=PORT, debug=DEBUG)
