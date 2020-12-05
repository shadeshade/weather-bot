from app import server
from app.credentials import SERVER_IP, PORT, DEBUG
from app.mastermind.scheduling import back_up_reminders
from app.views import set_webhook


def run_app():
    set_webhook()
    back_up_reminders()
    return server


if __name__ == '__main__':
    set_webhook()
    back_up_reminders()
    server.run(threaded=True, host=SERVER_IP, port=PORT, debug=DEBUG, use_reloader=False)
