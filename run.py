from weather_app import app
from weather_app.credentials import SERVER_IP, PORT, DEBUG
from weather_app.mastermind.scheduling import back_up_reminders
from weather_app.views import set_webhook

if __name__ == '__main__':
    set_webhook()
    back_up_reminders()
    app.run(threaded=True, host=SERVER_IP, port=PORT, debug=DEBUG, use_reloader=False)
