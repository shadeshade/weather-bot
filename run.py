from app import app, get_app
from app.mastermind.scheduling import back_up_reminders
from app.views import set_webhook
from app.credentials import SERVER_IP, PORT, DEBUG

server = get_app()

if __name__ == '__main__':
    set_webhook()
    back_up_reminders()
    app.run(threaded=True, host=SERVER_IP, port=PORT, debug=DEBUG, use_reloader=False)
