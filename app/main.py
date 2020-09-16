from time import sleep

import telebot
from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.schedulers.base import STATE_STOPPED, STATE_RUNNING
from flask import request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from app import app, db, bot
from app.data.lang_db import main_keyboard_lang as mkl
from app.data.lang_db import button_weather_now_lang as bwn
# from app.data.phenomena_db import phenomena_markups
from app.telegrambot.credentials import HEROKU_DEPLOY_DOMAIN, NGROK_DEPLOY_DOMAIN, TOKEN
from app.telegrambot.mastermind import *
from app.telegrambot.models import User, ReminderTime, PhenomenonTime, Phenomenon
from app.telegrambot.settings import DEBUG

sched = BackgroundScheduler()


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    bot.remove_webhook()
    sleep(1)
    if DEBUG:
        s = bot.set_webhook(f'{NGROK_DEPLOY_DOMAIN}/{TOKEN}')
    else:
        s = bot.set_webhook(f'{HEROKU_DEPLOY_DOMAIN}/{TOKEN}')

    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


# handle incoming messages
@app.route(f'/{TOKEN}', methods=['POST'])
def get_update():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok", 200


# Handle '/start'
@bot.message_handler(commands=['start'])
def command_start(message, ):
    user = User.query.filter_by(chat_id=message.chat.id).first()

    if not user:
        new_user = User(username=message.from_user.first_name, chat_id=message.chat.id,
                        language=message.from_user.language_code)
        db.session.add(new_user)
        db.session.commit()

    user_name = message.from_user.first_name
    lang = user.language or message.from_user.language_code
    response = get_start(user_name, lang)
    bot.send_message(message.chat.id, text=response, reply_markup=call_main_keyboard(lang), parse_mode='html')


# Handle button 'weather now'
@bot.message_handler(func=lambda message: message.text == mkl['en'][0] or message.text == mkl['ru'][0])
def button_weather_now(message, ):
    chat_id = message.chat.id
    user = User.query.filter_by(chat_id=chat_id).first()
    city = user.city_name
    lang = user.language
    response = get_response(city_name=city, lang=lang)
    bot.send_message(chat_id=chat_id, text=response, parse_mode='html')


# Handle button 'for tomorrow'
@bot.message_handler(func=lambda message: message.text == mkl['en'][1] or message.text == mkl['ru'][1])
def button_tomorrow(message, ):
    user = User.query.filter_by(chat_id=message.chat.id).first()
    city = user.city_name
    lang = user.language
    response = get_next_day(city, lang, cond_needed=False)
    bot.send_message(chat_id=message.chat.id, text=response, parse_mode='html')


# Handle button 'for a week'
@bot.message_handler(func=lambda message: message.text == mkl['en'][2] or message.text == mkl['ru'][2])
def button_week(message, ):
    cur_user = User.query.filter_by(chat_id=message.chat.id).first()
    city_name = cur_user.city_name
    response = get_next_week(city_name, cur_user.language)
    bot.send_message(chat_id=message.chat.id, text=response, parse_mode='html')


# Handle button 'settings'
@bot.message_handler(func=lambda message: message.text == mkl['en'][3] or message.text == mkl['ru'][3])
def button_settings(message, ):
    try:
        cur_user = User.query.filter_by(chat_id=message.chat.id).first()
        lang = cur_user.language
    except:
        lang = message.from_user.language_code
    bot.send_message(message.chat.id, text='Настройки', reply_markup=call_settings_keyboard(lang))


# Handle button 'daily'
@bot.message_handler(func=lambda message: message.text == mkl['en'][4] or message.text == mkl['ru'][4])
def command_daily(message):
    if not bool(User.query.filter_by(chat_id=message.chat.id).first()):
        return bot.send_message(message.chat.id, text='No city name was set up', )

    reminders = ReminderTime.query.all()
    for reminder in reminders:
        if reminder.hours is None or reminder.minutes is None:
            db.session.delete(reminder)
            db.session.commit()

    response = 'Set daily time you want to receive weather information'
    bot.send_message(message.chat.id, text=response, reply_markup=gen_markup_daily())


# Handle '/daily' (setting a daily reminder)
def set_daily(new_reminder, hours, minutes, ):
    # sched.add_job(daily_info, trigger='cron', hour=hours, minute=minutes, args=[new_reminder.user_id])
    if hours is None or minutes is None:
        db.session.delete(new_reminder)
        db.session.commit()
        return
    job = sched.add_job(daily_info, args=[new_reminder.user_id], trigger='cron', hour=hours, minute=minutes, )
    job_id = job.id
    new_reminder.job_id = job_id
    db.session.commit()

    print("added")
    sched.print_jobs()
    jobs = sched.get_jobs()
    print(jobs)
    print('end')
    # sched.get_job(1)
    if sched.state == 0:
        sched.start()


# Handle '/daily' (sending a reminder)
def daily_info(user_id):
    user = User.query.filter_by(id=user_id).first()
    city_name = user.city_name
    response = get_daily(city_name)
    bot.send_message(user.chat_id, text=response, )


# Handle button 'phenomenon'
@bot.message_handler(func=lambda message: message.text == mkl['en'][5] or message.text == mkl['ru'][5])
def button_phenomenon(message, ):
    response = 'Set a reminder about the incoming event you want. ' \
               'E.g. get notified that rain is expected tomorrow'
    bot.send_message(message.chat.id, text=response, reply_markup=gen_markup_phenomenon())


# Handle phenomenon reminder -
def set_phenomenon_time(hours, minutes, user_id):
    # delete_ph_time_jobs(user_id)
    # phenomenon_info_date = datetime.datetime.now()  # get from database column time
    job = sched.add_job(phenomenon_info, args=[user_id], trigger='cron', hour=hours, minute=minutes, )
    job_id = job.id
    new_reminder = PhenomenonTime.query.filter_by(user_id=user_id).first()
    new_reminder.job_id = job_id
    db.session.commit()

    print("added")
    sched.print_jobs()
    jobs = sched.get_jobs()
    print(jobs)
    print('end')

    if sched.state == 0:
        sched.start()


# Handle delete phenomenon reminder -
def delete_ph_time_jobs(user_id):
    try:
        ph_reminders = PhenomenonTime.query.filter_by(user_id=user_id).all()
        for reminder in ph_reminders:
            job_id = reminder.job_id
            sched.remove_job(job_id=job_id)
    except:
        pass


# Handle phenomenon reminder (sending a reminder) -
def phenomenon_info(user_id):
    cur_user = User.query.filter_by(id=user_id).first()
    language = cur_user.language
    all_phenomena = Phenomenon.query.filter_by(user_id=cur_user.id).all()
    text = get_next_day(cur_user.city_name, language, cond_needed=True)
    # text = {'part1': 'Fog', 'part2': 'Strong wind', 'part3': 'Clear', 'part4': 'Clear'}
    for phenomenon in all_phenomena:
        for t in text.values():
            if t.lower() in phenomenon.phenomenon.lower():
                bot.send_message(cur_user.chat_id, text=f'Tomorrow expected {t}', )


# Handle '/daily'
def remove_daily(job_id):
    sched.remove_job(job_id=job_id)


# Handle '/daily'
def back_up_reminders():
    sched.remove_all_jobs()

    reminders = ReminderTime.query.all()
    for reminder in reminders:
        set_daily(reminder, reminder.hours, reminder.minutes)

    phenomenon_reminders = PhenomenonTime.query.all()
    for ph_reminder in phenomenon_reminders:
        set_phenomenon_time(ph_reminder.hours, ph_reminder.minutes, ph_reminder.user_id)


# Handle button 'city'
@bot.message_handler(func=lambda message: message.text == mkl['en'][6] or message.text == mkl['ru'][6])
def button_city(message, ):
    response = 'Please, type the name of your city'
    bot.send_message(message.chat.id, text=response, )


# Handle button 'language'
@bot.message_handler(func=lambda message: message.text == mkl['en'][7] or message.text == mkl['ru'][7])
def button_language(message, ):
    response = 'Please, choose your language'
    bot.send_message(chat_id=message.chat.id, text=response, reply_markup=gen_markup_language())


# Handle button 'help'
@bot.message_handler(func=lambda message: message.text == mkl['en'][8] or message.text == mkl['ru'][8])
def command_help(message, ):
    response = get_help()
    bot.send_message(message.chat.id, text=response, )


# Handle button 'menu'
@bot.message_handler(func=lambda message: message.text == mkl['en'][9] or message.text == mkl['ru'][9])
def command_help(message, ):
    try:
        cur_user = User.query.filter_by(chat_id=message.chat.id).first()
        lang = cur_user.language
    except:
        lang = message.from_user.language_code
    bot.send_message(message.chat.id, text='Главное меню', reply_markup=call_main_keyboard(lang))


# Handle all other messages with content_type 'sticker' and 'text' (content_types defaults to ['text'])
@bot.message_handler(content_types=["sticker", "text"])
def respond(message):
    if message.sticker:
        sticker = open('app/static/AnimatedSticker.tgs', 'rb')
        return bot.send_sticker(message.chat.id, sticker)
    else:
        chat_id = message.chat.id
        user = User.query.filter_by(chat_id=chat_id).first()
        lang = user.language
        city = message.text
        response = get_response(city, lang)
        if 'Try again' not in response:
            user.city_name = city
            db.session.commit()
        return bot.send_message(chat_id=chat_id, text=response, parse_mode='html')


# handle main keyboard
def call_main_keyboard(lang):
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn1 = KeyboardButton(mkl[lang][0])
    btn2 = KeyboardButton(mkl[lang][1])
    btn3 = KeyboardButton(mkl[lang][2])
    btn4 = KeyboardButton(mkl[lang][3])
    keyboard.add(btn1, btn2, )
    keyboard.add(btn3, btn4, )
    return keyboard


# handle settings inline keyboard
def call_settings_keyboard(lang):
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn1 = KeyboardButton(mkl[lang][4])
    btn2 = KeyboardButton(mkl[lang][5])
    btn3 = KeyboardButton(mkl[lang][6])
    btn4 = KeyboardButton(mkl[lang][7])
    btn5 = KeyboardButton(mkl[lang][8])
    btn6 = KeyboardButton(mkl[lang][9])

    keyboard.add(btn1, btn2, )
    keyboard.add(btn3, btn4, )
    keyboard.add(btn5, )
    keyboard.add(btn6)
    return keyboard


# handle phenomenon inline keyboard -
def gen_markup_phenomenon():
    markup = InlineKeyboardMarkup(row_width=2)
    tick = '✖'
    markup.add(
        InlineKeyboardButton(f"{tick}Сильный ветер", callback_data="phenomenon strong wind"),
        InlineKeyboardButton(f"{tick}Град", callback_data="phenomenon hailstorm"),
        InlineKeyboardButton(f"{tick}Ураган", callback_data="phenomenon hurricane"),
        InlineKeyboardButton(f"{tick}Гроза", callback_data="phenomenon storm"),
        InlineKeyboardButton(f"{tick}Дождь", callback_data="phenomenon rain"),
        InlineKeyboardButton(f"{tick}Сильный ливень", callback_data="phenomenon heavy rain"),
        InlineKeyboardButton(f"{tick}Туман", callback_data="phenomenon fog"),
        InlineKeyboardButton(f"{tick}Сильная жара", callback_data="phenomenon intense heat"),
        InlineKeyboardButton(f"{tick}Все события", callback_data="phenomenon all"),
        InlineKeyboardButton("Изменить время", callback_data="phenomenon time"),
    )
    return markup


# handle phenomenon inline keyboard time setting (hours) -
@bot.callback_query_handler(func=lambda call: call.data == "back_to_hours_ph" or call.data == "phenomenon time")
def callback_phenomenon_keyboard(call):
    try:
        user_id = User.query.filter_by(chat_id=call.from_user.id).first()
        user_id = user_id.id
        ph_reminders = PhenomenonTime.query.filter_by(user_id=user_id, minutes=None).all()
        for reminder in ph_reminders:
            db.session.delete(reminder)
        db.session.commit()
    except:
        pass

    markup = InlineKeyboardMarkup(row_width=4)
    markup.add(
        InlineKeyboardButton("✖00:00", callback_data="0hr_ph"), InlineKeyboardButton("✖01:00", callback_data="1hr_ph"),
        InlineKeyboardButton("✖02:00", callback_data="2hr_ph"), InlineKeyboardButton("✖03:00", callback_data="3hr_ph"),
        InlineKeyboardButton("✖04:00", callback_data="4hr_ph"), InlineKeyboardButton("✖05:00", callback_data="5hr_ph"),
        InlineKeyboardButton("✖06:00", callback_data="6hr_ph"), InlineKeyboardButton("✖07:00", callback_data="7hr_ph"),
        InlineKeyboardButton("✖08:00", callback_data="8hr_ph"), InlineKeyboardButton("✖09:00", callback_data="9hr_ph"),
        InlineKeyboardButton("✖10:00", callback_data="10hr_ph"),
        InlineKeyboardButton("✖11:00", callback_data="11hr_ph"),
        InlineKeyboardButton("✖12:00", callback_data="12hr_ph"),
        InlineKeyboardButton("✖13:00", callback_data="13hr_ph"),
        InlineKeyboardButton("✖14:00", callback_data="14hr_ph"),
        InlineKeyboardButton("✖15:00", callback_data="15hr_ph"),
        InlineKeyboardButton("✖16:00", callback_data="16hr_ph"),
        InlineKeyboardButton("✖17:00", callback_data="17hr_ph"),
        InlineKeyboardButton("✖18:00", callback_data="18hr_ph"),
        InlineKeyboardButton("✖19:00", callback_data="19hr_ph"),
        InlineKeyboardButton("✖20:00", callback_data="20hr_ph"),
        InlineKeyboardButton("✖21:00", callback_data="21hr_ph"),
        InlineKeyboardButton("✖22:00", callback_data="22hr_ph"),
        InlineKeyboardButton("✖23:00", callback_data="23hr_ph"),
        InlineKeyboardButton("↩ Back", callback_data="back_to_ph"),

    )

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Set the time you want to receive phenomenon information",
                          reply_markup=markup)


# handle phenomenon inline keyboard time setting (hours) -
@bot.callback_query_handler(func=lambda call: 'hr_ph' in call.data)
def callback_phenomenon_hr(call):
    """
        writing phenomenon hours data to db
    """
    user_id = User.query.filter_by(chat_id=call.from_user.id).first()
    user_id = user_id.id

    phenomenon_hours = call.data[:-5]
    new_phenomenon = PhenomenonTime(hours=phenomenon_hours, user_id=user_id)
    db.session.add(new_phenomenon)
    db.session.commit()

    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(InlineKeyboardButton("✖00:00", callback_data="00min_ph"),
               InlineKeyboardButton("✖00:10", callback_data="10min_ph"),
               InlineKeyboardButton("✖00:20", callback_data="20min_ph"),
               InlineKeyboardButton("✖00:30", callback_data="30min_ph"),
               InlineKeyboardButton("✖00:40", callback_data="40min_ph"),
               InlineKeyboardButton("✖00:50", callback_data="50min_ph"),
               InlineKeyboardButton("↩ Back", callback_data="back_to_hours_ph"),
               )

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Set the time you want to receive phenomenon info",
                          reply_markup=markup)


# handle phenomenon inline keyboard -
@bot.callback_query_handler(func=lambda call: 'min_ph' in call.data)
def callback_phenomenon_min(call):
    """
    writing phenomenon minutes data to db
    """
    user_id = User.query.filter_by(chat_id=call.from_user.id).first()
    user_id = user_id.id

    phenomenon_minutes = call.data[:-6]
    new_phenomenon = PhenomenonTime.query.filter_by(user_id=user_id).order_by(PhenomenonTime.id.desc()).first()
    if int(phenomenon_minutes) == new_phenomenon.minutes:
        phenomenon_minutes = None
    phenomenon_hours = new_phenomenon.hours
    delete_ph_time_jobs(user_id)
    new_phenomenon = PhenomenonTime(user_id=user_id, hours=phenomenon_hours, minutes=phenomenon_minutes)
    ph_reminders = PhenomenonTime.query.filter_by(user_id=user_id).all()
    for reminder in ph_reminders:
        db.session.delete(reminder)
    db.session.add(new_phenomenon)
    db.session.commit()
    ph_hours = new_phenomenon.hours
    ph_minutes = new_phenomenon.minutes
    if ph_minutes is not None:
        set_phenomenon_time(ph_hours, ph_minutes, user_id)

    print("added")
    sched.print_jobs()
    print('end')

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f"Schedule was set up at {phenomenon_hours}:{phenomenon_minutes}")

    bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                              text=f"Schedule was set up at {phenomenon_hours}:{phenomenon_minutes}")


# handle phenomenon db -
@bot.callback_query_handler(func=lambda call: 'phenomenon' in call.data)
def callback_phenomenon(call):
    """"add phenomenon to db"""
    cur_user = User.query.filter_by(chat_id=call.from_user.id).first()
    user_id = cur_user.id
    phenomenon_data = call.data
    # ph_time = PhenomenonTime.query.filter_by(user_id=user_id).first()
    # ph_hours = ph_time.hours
    # ph_minutes = ph_time.minutes
    new_phenomenon = Phenomenon.query.filter_by(phenomenon=phenomenon_data, user_id=user_id).first()
    try:
        db.session.delete(new_phenomenon)
    except:
        new_phenomenon = Phenomenon(phenomenon=phenomenon_data, user_id=user_id)
        db.session.add(new_phenomenon)
    db.session.commit()
    # set_phenomenon_time(new_phenomenon, ph_hours, ph_minutes)


# handle back to phenomenon button
@bot.callback_query_handler(func=lambda call: call.data == "back_to_ph")
def callback_inline_back_ph(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="test",
                          reply_markup=gen_markup_phenomenon())


# handle language inline keyboard
def gen_markup_language():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✖English", callback_data="english"),
        InlineKeyboardButton("✖Русский", callback_data="russian"),
    )
    return markup


# handle language button
@bot.callback_query_handler(func=lambda call: call.data == "english" or call.data == "russian")
def callback_inline_back_ph(call):
    user = User.query.filter_by(chat_id=call.message.chat.id).first()
    new_lang = call.data
    user.language = new_lang[:2]
    db.session.commit()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f'{new_lang.title()} has been chosen')


# handle daily inline keyboard
def gen_markup_daily():
    markup = InlineKeyboardMarkup(row_width=4)
    # ✖️✔️
    markup.add(
        InlineKeyboardButton("✖00:00", callback_data="0hr"), InlineKeyboardButton("✖01:00", callback_data="1hr"),
        InlineKeyboardButton("✖02:00", callback_data="2hr"), InlineKeyboardButton("✖03:00", callback_data="3hr"),
        InlineKeyboardButton("✖04:00", callback_data="4hr"), InlineKeyboardButton("✖05:00", callback_data="5hr"),
        InlineKeyboardButton("✖06:00", callback_data="6hr"), InlineKeyboardButton("✖07:00", callback_data="7hr"),
        InlineKeyboardButton("✖08:00", callback_data="8hr"), InlineKeyboardButton("✖09:00", callback_data="9hr"),
        InlineKeyboardButton("✖10:00", callback_data="10hr"), InlineKeyboardButton("✖11:00", callback_data="11hr"),
        InlineKeyboardButton("✖12:00", callback_data="12hr"), InlineKeyboardButton("✖13:00", callback_data="13hr"),
        InlineKeyboardButton("✖14:00", callback_data="14hr"), InlineKeyboardButton("✖15:00", callback_data="15hr"),
        InlineKeyboardButton("✖16:00", callback_data="16hr"), InlineKeyboardButton("✖17:00", callback_data="17hr"),
        InlineKeyboardButton("✖18:00", callback_data="18hr"), InlineKeyboardButton("✖19:00", callback_data="19hr"),
        InlineKeyboardButton("✖20:00", callback_data="20hr"), InlineKeyboardButton("✖21:00", callback_data="21hr"),
        InlineKeyboardButton("✖22:00", callback_data="22hr"), InlineKeyboardButton("✖23:00", callback_data="23hr"),
    )
    return markup


# handle daily inline keyboard (hours)
@bot.callback_query_handler(func=lambda call: "hr" in call.data)
def callback_inline_daily_min(call):
    """
    writing hours data to db and changing keyboard
    """
    cur_user = User.query.filter_by(chat_id=call.from_user.id).first()
    user_id = cur_user.id

    reminder_hours = call.data[:-2]
    new_reminder = ReminderTime(hours=reminder_hours, user_id=user_id)
    db.session.add(new_reminder)
    db.session.commit()

    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(InlineKeyboardButton("✖00:00", callback_data="00min"),
               InlineKeyboardButton("✖00:10", callback_data="10min"),
               InlineKeyboardButton("✖00:20", callback_data="20min"),
               InlineKeyboardButton("✖00:30", callback_data="30min"),
               InlineKeyboardButton("✖00:40", callback_data="40min"),
               InlineKeyboardButton("✖00:50", callback_data="50min"),
               InlineKeyboardButton("↩ Back", callback_data="back_to_hours"),
               )

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Set daily time you want to receive weather information",
                          reply_markup=markup)


# handle daily inline keyboard (minutes)
@bot.callback_query_handler(func=lambda call: 'min' in call.data)
def callback_inline_daily(call):
    """
    writing minutes data to db
    """
    user_id = User.query.filter_by(chat_id=call.from_user.id).first()
    user_id = user_id.id

    reminder_minutes = call.data[:-3]
    new_reminder = ReminderTime.query.filter_by(user_id=user_id).order_by(ReminderTime.id.desc()).first()

    reminder_hours = new_reminder.hours

    existing_reminder = ReminderTime.query.filter_by(user_id=user_id, hours=reminder_hours,
                                                     minutes=reminder_minutes).first()
    if existing_reminder is not None:  # if reminder exists
        reminder_job_id = existing_reminder.job_id
        db.session.delete(existing_reminder)
        db.session.commit()

        reminders = ReminderTime.query.all()
        for reminder in reminders:
            if reminder.hours is None or reminder.minutes is None:
                db.session.delete(reminder)
                db.session.commit()

        remove_daily(job_id=reminder_job_id)
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="The time was deleted")


    else:  # if reminder does not exist

        new_reminder.minutes = reminder_minutes
        # db.session.add(new_reminder)
        db.session.commit()
        set_daily(new_reminder, reminder_hours, reminder_minutes, )

    # bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
    #                       text=f"Schedule was set up at {new_reminder.hours}:{new_reminder.minutes}")

    bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                              text=f"Schedule was set up at {reminder_hours}:{reminder_minutes}")


# handle back to hours button
@bot.callback_query_handler(func=lambda call: call.data == "back_to_hours")
def callback_inline_back(call):
    try:
        user_id = User.query.filter_by(chat_id=call.from_user.id).first()
        user_id = user_id.id

        reminder = ReminderTime.query.filter_by(minutes=None, user_id=user_id).first()
        db.session.delete(reminder)
        db.session.commit()
    except:
        pass

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Set daily time you want to receive weather information",
                          reply_markup=gen_markup_daily())
