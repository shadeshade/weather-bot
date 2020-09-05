from app import app
from app.main import set_webhook, sched
from app.telegrambot.settings import SERVER_IP, PORT, DEBUG
from app.main import back_up_reminders

if __name__ == '__main__':
    set_webhook()
    print("up")
    sched.print_jobs()
    print('end')
    back_up_reminders()
    app.run(threaded=True, host=SERVER_IP, port=PORT, debug=DEBUG)
