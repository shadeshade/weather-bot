from app import server
from app.main import set_webhook
from app.telegrambot.settings import SERVER_IP, PORT, DEBUG

if __name__ == '__main__':
    # set_webhook()
    server.run(threaded=True, host=SERVER_IP, port=PORT, debug=DEBUG)
