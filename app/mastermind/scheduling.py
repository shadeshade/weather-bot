from apscheduler.schedulers.background import BackgroundScheduler

from app import bot, db
from app.mastermind.formating import get_response, get_phenomenon_info
from app.models import User, PhenomenonTime, ReminderTime

sched = BackgroundScheduler()


# Handle '/daily' (setting a daily reminder)
def set_daily(new_reminder, hours, minutes, ):
    job = sched.add_job(
        daily_info, args=[new_reminder.user_id, f'{hours}.{minutes}'],
        trigger='cron', hour=hours, minute=minutes
    )
    job_id = job.id
    new_reminder.job_id = job_id
    db.session.commit()

    if sched.state == 0:
        sched.start()


# Handle '/daily' (sending a reminder)
def daily_info(user_id, set_time):
    user = User.query.filter_by(id=user_id).first()
    response = get_response(user.city_name, user.language, set_time)

    bot.send_message(user.chat_id, text=response, parse_mode='html')


# Handle phenomenon reminder
def set_phenomenon_time(new_reminder, hours, minutes):
    user_id = new_reminder.user_id
    job = sched.add_job(send_phenomenon_reminder, args=[user_id],
                        trigger='cron', hour=hours, minute=minutes, )
    new_reminder.job_id = job.id
    db.session.commit()

    if sched.state == 0:
        sched.start()


def send_phenomenon_reminder(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    response_msg = get_phenomenon_info(user)
    if response_msg:
        bot.send_message(user.chat_id, text=response_msg, parse_mode='html')


# Handle delete phenomenon reminder
def delete_ph_time_jobs(user_id):
    ph_reminders = PhenomenonTime.query.filter_by(user_id=user_id).all()
    for reminder in ph_reminders:
        sched.remove_job(job_id=reminder.job_id)


# Handle '/daily'
def back_up_reminders():
    sched.remove_all_jobs()

    reminders = ReminderTime.query.all()
    for reminder in reminders:
        set_daily(reminder, reminder.hours, reminder.minutes)

    phenomenon_reminders = PhenomenonTime.query.all()
    for ph_reminder in phenomenon_reminders:
        set_phenomenon_time(ph_reminder, ph_reminder.hours, ph_reminder.minutes)

