from time import sleep

from flask import Flask, request
import telegram
from telebot.credentials import TOKEN
from telebot.mastermind import get_response
from telebot.settings import *

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

# if DEBUG:
#     bot.set_webhook(url="https://{}:{}/{}".format(SERVER_IP, PORT, TOKEN),
#                     certificate=open('./SSL_certs/localhost_crt.pem', 'rb'))
# else:
#     bot.set_webhook(url="https://{}/{}".format(DEPLOY_DOMAIN, TOKEN))



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


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook(f'{DEPLOY_DOMAIN}{TOKEN}')
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


if __name__ == '__main__':
    if DEBUG:
        app.run(host=HOST, port=PORT, debug=True,
                ssl_context=('./SSL_certs/localhost_crt.pem', './SSL_certs/localhost_key.pem'))
    else:
        # app.run(host=HOST, port=PORT)
        app.run(threaded=True)
