from app import server
from app.credentials import SERVER_IP, PORT, DEBUG
from app.mastermind.formating import get_phenomenon_info
from app.mastermind.scheduling import back_up_reminders, sched
from app.models import User
from app.views import set_webhook

if __name__ == '__main__':
    set_webhook()
    back_up_reminders()

    # u = User.query.filter_by(id=1).first()
    # get_phenomenon_info(u)

    server.run(threaded=True, host=SERVER_IP, port=PORT, debug=DEBUG, use_reloader=False)
