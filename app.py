from flask import Flask, request
import schedule
from threading import Thread
from time import sleep
import telegram
from apscheduler.schedulers.background import BackgroundScheduler

from telebot.credentials import TOKEN, HEROKU_DEPLOY_DOMAIN, NGROK_DEPLOY_DOMAIN
from telebot.mastermind import *
from telebot.settings import DEBUG, PORT, SERVER_IP

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

scheduler = BackgroundScheduler()


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

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode('utf-8').decode()
    print("got text message :", text)

    if text == '/start':
        first_name = update.message.chat.first_name
        response = start_command(first_name)
    elif text == '/help':
        response = help_command()
    elif text == '/daily':
        daily()
        response = 'Schedule was set up'


    else:
        response = get_response(text)

    bot.sendMessage(chat_id=chat_id, text=response, )
    return 'ok'


def daily():
    try:
        scheduler.remove_all_jobs()
        scheduler.add_job(daily_info, trigger='interval', seconds=6, )
        scheduler.start()
    except:
        pass

def daily_info(chat_id=272700497):
    text_ = 11
    return bot.sendMessage(chat_id=chat_id, text=text_, )


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
