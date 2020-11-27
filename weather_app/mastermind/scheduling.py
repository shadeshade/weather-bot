from apscheduler.schedulers.background import BackgroundScheduler

from weather_app import bot, db
from weather_app.mastermind.formating import get_today_weather_info, get_phenomenon_info
from weather_app.models import User, ReminderTime

sched = BackgroundScheduler()


# Handle '/daily' (setting a daily reminder)
def set_daily(new_reminder, hours, minutes, ):
    job = sched.add_job(
        send_daily_info, args=[new_reminder.user_id, f'{hours}.{minutes}'],
        trigger='cron', hour=hours, minute=minutes
    )
    job_id = job.id
    new_reminder.job_id = job_id
    db.session.commit()

    if sched.state == 0:
        sched.start()


# Handle '/daily' (sending a reminder)
def send_daily_info(user_id, set_time):
    user = User.query.filter_by(id=user_id).first()
    response = get_today_weather_info(user.city_name, user.language, set_time)

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


# Handle '/phenomena' (sending a phenomenon reminder)
def send_phenomenon_reminder(user_id):
    user = User.query.filter_by(id=user_id).first()
    response_msg = get_phenomenon_info(user)
    if response_msg:
        bot.send_message(user.chat_id, text=response_msg, parse_mode='html')


# Handle delete phenomenon reminder
def delete_ph_time_jobs(user_id):
    ph_reminders = ReminderTime.query.filter_by(user_id=user_id, is_phenomenon=True).all()
    for reminder in ph_reminders:
        sched.remove_job(job_id=reminder.job_id)


def back_up_reminders():
    """Handle buttons 'daily' and 'phenomena'"""
    sched.remove_all_jobs()
    all_reminders = ReminderTime.query.filter_by().all()

    # daily_reminders = ReminderTime.query.filter_by(is_phenomenon=False).all()
    daily_reminders = [reminder for reminder in all_reminders if reminder.is_phenomenon is False]
    for reminder in daily_reminders:
        set_daily(reminder, reminder.hours, reminder.minutes)

    # phenomenon_reminders = ReminderTime.query.filter_by(is_phenomenon=True).all()
    phenomenon_reminders = [reminder for reminder in all_reminders if reminder.is_phenomenon is True]
    for ph_reminder in phenomenon_reminders:
        set_phenomenon_time(ph_reminder, ph_reminder.hours, ph_reminder.minutes)


if __name__ == '__main__':
    send_phenomenon_reminder(1)
