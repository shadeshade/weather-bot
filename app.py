from flask import Flask, request
import telegram
from telebot.credentials import bot_token, bot_user_name, URL
from telebot.mastermind import get_response

global bot
global TOKEN
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)
bot.setWebhook(f'{URL}{TOKEN}')

app = Flask(__name__)


@app.route(f'/{TOKEN}', methods=['POST'])
def respond():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode('utf-8').decode()
    print("got text message :", text)

    response = get_response(text)
    bot.sendMessage(chat_id=chat_id, text=response, )

    return 'ok'


# @app.route('/setwebhook', methods=['GET', 'POST'])
# def set_webhook():
#     s =
#     if s:
#         return "webhook setup ok"
#     else:
#         return "webhook setup failed"


if __name__ == '__main__':
    app.run(threaded=True)
