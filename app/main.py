# from time import sleep

import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from flask import request

from app import app, db, bot
from app.data.localization import buttons, inline_buttons
from app.data.tele_buttons import phenomena_list, gen_markup_minutes, gen_markup_hours, gen_markup_phenomena, \
    gen_markup_language, call_main_keyboard, call_settings_keyboard
from app.telegrambot.credentials import HEROKU_DEPLOY_DOMAIN, NGROK_DEPLOY_DOMAIN, TOKEN
from app.telegrambot.mastermind import *
from app.telegrambot.models import User, ReminderTime, PhenomenonTime, Phenomenon
from app.telegrambot.settings import DEBUG

sched = BackgroundScheduler()


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    bot.remove_webhook()
    # sleep(1)
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
@bot.message_handler(
    func=lambda message: message.text == buttons['weather now']['en'] or message.text == buttons['weather now']['ru'])
def button_weather_now(message, ):
    chat_id = message.chat.id
    user = User.query.filter_by(chat_id=chat_id).first()
    try:
        lang = user.language
    except:
        lang = message.from_user.language_code
    try:
        city = user.city_name
    except:
        return bot.send_message(chat_id=chat_id, text=hints['no city'][lang], parse_mode='html')

    response = get_response(city, lang, message.date)
    bot.send_message(chat_id=chat_id, text=response, parse_mode='html')


# Handle button 'for tomorrow'
@bot.message_handler(
    func=lambda message: message.text == buttons['for tomorrow']['en'] or message.text == buttons['for tomorrow']['ru'])
def button_tomorrow(message, ):
    chat_id = message.chat.id
    user = User.query.filter_by(chat_id=message.chat.id).first()
    try:
        lang = user.language
    except:
        lang = message.from_user.language_code
    try:
        city = user.city_name
    except:
        return bot.send_message(chat_id=chat_id, text=hints['no city'][lang], parse_mode='html')

    response = get_next_day(city, lang, phenomenon_info=False)
    bot.send_message(chat_id=chat_id, text=response, parse_mode='html')


# Handle button 'for a week'
@bot.message_handler(
    func=lambda message: message.text == buttons['for a week']['en'] or message.text == buttons['for a week']['ru'])
def button_week(message, ):
    chat_id = message.chat.id
    user = User.query.filter_by(chat_id=chat_id).first()

    try:
        lang = user.language
    except:
        lang = message.from_user.language_code
    try:
        city = user.city_name
    except:
        return bot.send_message(chat_id=message.chat.id, text=hints['no city'][lang], parse_mode='html')

    response = get_next_week(city=city, lang=lang)
    bot.send_message(chat_id=chat_id, text=response, parse_mode='html')


# Handle button 'settings'
@bot.message_handler(
    func=lambda message: message.text == buttons['settings']['en'] or message.text == buttons['settings']['ru'])
def button_settings(message, ):
    chat_id = message.chat.id
    try:
        cur_user = User.query.filter_by(chat_id=chat_id).first()
        lang = cur_user.language
    except:
        lang = message.from_user.language_code
    bot.send_message(chat_id, text=info[lang][9], reply_markup=call_settings_keyboard(lang))


# Handle button 'daily'
@bot.message_handler(
    func=lambda message: message.text == buttons['daily']['en'] or message.text == buttons['daily']['ru'])
def button_daily(message):
    chat_id = message.chat.id
    user = User.query.filter_by(chat_id=chat_id).first()
    try:
        lang = user.language
    except:
        lang = message.from_user.language_code

    if not user or not user.city_name:
        return bot.send_message(chat_id, hints['no city'][lang])

    reminders = ReminderTime.query.all()
    for reminder in reminders:
        if reminder.hours is None or reminder.minutes is None:
            db.session.delete(reminder)
            db.session.commit()
    response = hints['time daily'][lang]
    bot.send_message(chat_id, text=response, reply_markup=gen_markup_daily(user.id))


# Handle '/daily' (setting a daily reminder)
def set_daily(new_reminder, hours, minutes, ):
    if hours is None or minutes is None:
        db.session.delete(new_reminder)
        db.session.commit()
        return
    job = sched.add_job(
        daily_info, args=[new_reminder.user_id, f'{hours}.{minutes}'], trigger='cron', hour=hours, minute=minutes
    )
    job_id = job.id
    new_reminder.job_id = job_id
    db.session.commit()

    print("added")
    sched.print_jobs()
    jobs = sched.get_jobs()
    print(jobs)
    print('end')

    if sched.state == 0:
        sched.start()


# Handle '/daily' (sending a reminder)
def daily_info(user_id, set_time):
    user = User.query.filter_by(id=user_id).first()
    response = get_response(user.city_name, user.language, set_time)

    bot.send_message(user.chat_id, text=response, parse_mode='html')


# Handle button 'phenomena'
@bot.message_handler(
    func=lambda message: message.text == buttons['phenomena']['en'] or message.text == buttons['phenomena']['ru'])
def button_phenomena(message, ):
    chat_id = message.chat.id
    user = User.query.filter_by(chat_id=chat_id).first()

    try:
        lang = user.language
    except:
        lang = message.from_user.language_code

    if not user or not user.city_name:
        return bot.send_message(chat_id, hints['no city'][lang])

    response = hints['phenomena intro'][lang]
    bot.send_message(message.chat.id, text=response, reply_markup=gen_markup_phenomena(user.id, lang))


# Handle phenomenon reminder
def set_phenomenon_time(hours, minutes, user_id):
    job = sched.add_job(phenomenon_info, args=[user_id], trigger='cron', hour=hours, minute=minutes, )
    new_reminder = PhenomenonTime.query.filter_by(user_id=user_id).first()
    new_reminder.job_id = job.id
    db.session.commit()
    if sched.state == 0:
        sched.start()


# Handle delete phenomenon reminder
def delete_ph_time_jobs(user_id):
    ph_reminders = PhenomenonTime.query.filter_by(user_id=user_id).all()
    for reminder in ph_reminders:
        sched.remove_job(job_id=reminder.job_id)


# Handle phenomenon reminder (sending a reminder)
def phenomenon_info(user_id):
    user = User.query.filter_by(id=user_id).first()
    lang = user.language
    all_phenomena = Phenomenon.query.filter_by(user_id=user.id).all()
    next_day_info = get_next_day(user.city_name, user.language, phenomenon_info=True)
    next_day_dict = {'daypart_temp_positive': 0, 'daypart_temp_negative': 0, 'daypart_condition': [], 'daypart_wind': 0}
    for day_dart_info in next_day_info.values():
        if '+' in day_dart_info['weather_daypart_temp']:
            daypart_temp_positive = int(day_dart_info['weather_daypart_temp'].split('+')[-1].replace('°', ''))
            if daypart_temp_positive > next_day_dict['daypart_temp_positive']:
                next_day_dict['daypart_temp_positive'] = daypart_temp_positive
        elif '-' in day_dart_info['weather_daypart_temp']:
            daypart_temp_negative = int(day_dart_info['weather_daypart_temp'].split('-')[-1].replace('°', ''))
            if daypart_temp_negative > next_day_dict['daypart_temp_negative']:
                next_day_dict['daypart_temp_negative'] = daypart_temp_negative

        daypart_condition = day_dart_info['weather_daypart_condition']
        next_day_dict['daypart_condition'] += [daypart_condition.lower()]

        daypart_wind = float(day_dart_info['weather_daypart_wind'].replace(',', '.'))
        if daypart_wind > next_day_dict['daypart_wind']:
            next_day_dict['daypart_wind'] = daypart_wind

    daypart_temp_positive = next_day_dict['daypart_temp']
    daypart_condition = next_day_dict['daypart_condition']
    daypart_wind = next_day_dict['daypart_wind']

    for phenomenon in all_phenomena:
        existing_phenomenon = phenomenon.phenomenon
        if existing_phenomenon in daypart_condition:
            pass
        elif existing_phenomenon == "strong wind":
            if 29 >= daypart_wind >= 12:
                pass
            else:
                continue
        elif existing_phenomenon == "hurricane":
            if daypart_wind >= 30:
                pass
            else:
                continue
        elif existing_phenomenon == "intense heat":
            if daypart_temp_positive:
                if daypart_temp_positive >= 30:
                    pass
                else:
                    continue
            else:
                continue
        # elif existing_phenomenon == "intense heat":
        #     if daypart_temp_positive:
        #         if daypart_temp_positive >= 30:
        #             pass
        #         else:
        #             continue
        #     else:
        #         continue
        else:
            continue

        if lang == 'ru':
            response_message = f'{hints["phenomenon tomorrow"][user.language]} {existing_phenomenon}'
        else:
            response_message = f'{existing_phenomenon.capitalize()} {hints["phenomenon tomorrow"][user.language]}'
        bot.send_message(user.chat_id, text=response_message)


# # Handle '/daily'
# def remove_daily(job_id):
#     sched.remove_job(job_id=job_id)


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
@bot.message_handler(
    func=lambda message: message.text == buttons['city']['en'] or message.text == buttons['city']['ru'])
def button_city(message, intro=True):
    chat_id = message.chat.id
    user = User.query.filter_by(chat_id=chat_id).first()
    try:
        lang = user.language
    except:
        new_user = User(username=message.from_user.first_name, chat_id=chat_id, language=message.from_user.language_code)
        db.session.add(new_user)
        db.session.commit()
        lang = new_user.language
    if intro:
        text = hints['city intro'][lang]
    else:
        text = info[lang][0]
    sent = bot.send_message(chat_id=chat_id, text=text)
    bot.register_next_step_handler(message=sent, callback=add_city)


def add_city(message):
    chat_id = message.chat.id
    user = User.query.filter_by(chat_id=chat_id).first()
    lang = user.language
    city = message.text

    btns = {value[lang] for key, value in buttons.items()}
    inline_btns = {value[lang] for key, value in inline_buttons.items()}
    if message.text in btns or message.text in inline_btns:
        return

    response = get_response(city, lang, message.date)

    if info[lang][0] not in response:
        user.city_name = city
        db.session.commit()
        return bot.send_message(chat_id=chat_id, text=f"{hints['city added'][lang]}")
    elif info[lang][0] in response:
        bot.send_message(chat_id=chat_id, text=f"{hints['city fail'][lang]}")
        return button_city(message, intro=False)


# Handle button 'language'
@bot.message_handler(
    func=lambda message: message.text == buttons['language']['en'] or message.text == buttons['language']['ru'])
def button_language(message, ):
    chat_id = message.chat.id
    user = User.query.filter_by(chat_id=chat_id).first()
    try:
        lang = user.language
    except:
        new_user = User(username=message.from_user.first_name, chat_id=chat_id, language=message.from_user.language_code)
        db.session.add(new_user)
        db.session.commit()
        lang = new_user.language

    response = hints['lang intro'][lang]
    bot.send_message(chat_id=message.chat.id, text=response, reply_markup=gen_markup_language())


# Handle button 'help'
@bot.message_handler(
    func=lambda message: message.text == buttons['help']['en'] or message.text == buttons['help']['ru'])
def command_help(message, ):
    user = User.query.filter_by(chat_id=message.chat.id).first()
    response = get_help(user.language)
    bot.send_message(message.chat.id, text=response, parse_mode='html')


# Handle button 'menu'
@bot.message_handler(
    func=lambda message: message.text == buttons['menu']['en'] or message.text == buttons['menu']['ru'])
def button_menu(message, ):
    try:
        cur_user = User.query.filter_by(chat_id=message.chat.id).first()
        lang = cur_user.language
    except:
        lang = message.from_user.language_code
    bot.send_message(message.chat.id, text=hints['menu'][lang], reply_markup=call_main_keyboard(lang))


# Handle all other messages with content_type 'sticker' and 'text' (content_types defaults to ['text'])
@bot.message_handler(content_types=["sticker", "text"])
def respond(message):
    if message.sticker:
        sticker = open('app/static/AnimatedSticker.tgs', 'rb')
        return bot.send_sticker(message.chat.id, sticker)
    else:
        chat_id = message.chat.id
        user = User.query.filter_by(chat_id=chat_id).first()
        try:
            lang = user.language
        except:
            lang = message.from_user.language_code
        city = message.text
        response = get_response(city, lang, message.date)


        if not user:
            if 'Try again' not in response:
                user = User(username=message.from_user.first_name, chat_id=chat_id, city_name=city, language=lang)
                db.session.add(user)
                db.session.commit()
        return bot.send_message(chat_id=chat_id, text=response, parse_mode='html')


# handle phenomenon inline keyboard time setting (hours)
@bot.callback_query_handler(func=lambda call: call.data == "back_to_hours_ph" or call.data == "set time phenomena")
def callback_phenomenon_time(call):
    """imported temp_buttons"""

    user = User.query.filter_by(chat_id=call.from_user.id).first()
    lang = user.language
    user_id = user.id

    try:
        ph_reminders = PhenomenonTime.query.filter_by(user_id=user_id, minutes=None).all()
        for reminder in ph_reminders:
            db.session.delete(reminder)
        db.session.commit()
    except:
        pass

    markup = gen_markup_hours(user_id=user_id, model=PhenomenonTime, lang=lang, callback='_ph')

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=hints['phenomena time'][lang], reply_markup=markup)


# handle phenomenon inline keyboard time setting (minutes)
@bot.callback_query_handler(func=lambda call: 'hr_ph' in call.data)
def callback_phenomenon_hr(call):
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    user_id = user.id
    lang = user.language
    hours = call.data[:2]

    markup = gen_markup_minutes(user_id=user_id, hours=hours, model=PhenomenonTime, callback='_ph', lang=lang)

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=hints['phenomena time'][lang], reply_markup=markup)


# handle phenomenon inline keyboard
@bot.callback_query_handler(func=lambda call: 'min_ph' in call.data)
def callback_phenomenon_min(call):
    """writing phenomenon time to db"""
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    user_id = user.id
    lang = user.language

    phenomenon_hours = call.data[:2]
    phenomenon_minutes = call.data[3:5]

    existing_phenomenon = PhenomenonTime.query.filter_by(user_id=user_id, hours=phenomenon_hours,
                                                         minutes=phenomenon_minutes).first()

    delete_ph_time_jobs(user_id)
    ph_reminders = PhenomenonTime.query.filter_by(user_id=user_id).all()
    for reminder in ph_reminders:
        db.session.delete(reminder)

    if existing_phenomenon:
        # db.session.delete(existing_phenomenon)
        text = f"{hints['schedule delete'][lang]}"
    else:
        new_phenomenon = PhenomenonTime(user_id=user_id, hours=phenomenon_hours, minutes=phenomenon_minutes)
        db.session.add(new_phenomenon)
        set_phenomenon_time(new_phenomenon.hours, new_phenomenon.minutes, user_id)
        text = f"{hints['schedule set'][lang]} {phenomenon_hours}:{phenomenon_minutes}"

    db.session.commit()

    callback_phenomenon_hr(call)
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=text)


# handle all phenomena db
@bot.callback_query_handler(func=lambda call: call.data == "all phenomena")
def callback_all_phenomena(call):
    """"add all phenomena to db
    imported phenomena list"""
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    user_id = user.id
    lang = user.language

    phenomena_data = Phenomenon.query.filter_by(user_id=user_id).all()
    if len(phenomena_data) > 7:
        for ph in phenomena_data:
            db.session.delete(ph)
        text = hints['all untick'][lang]
    else:
        for ph in phenomena_list:
            new_phenomenon = Phenomenon.query.filter_by(phenomenon=ph, user_id=user_id).first()
            if new_phenomenon is None:
                new_phenomenon = Phenomenon(user_id=user_id, phenomenon=ph)
                db.session.add(new_phenomenon)
        text = hints['all tick'][lang]
    db.session.commit()

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=hints['phenomena intro'][lang], reply_markup=gen_markup_phenomena(user.id, lang))
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=text)


# handle phenomenon db
@bot.callback_query_handler(func=lambda call: 'phenomenon' in call.data)
def callback_phenomenon(call):
    """"add phenomenon to db"""
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    user_id = user.id
    lang = user.language
    phenomenon_data = call.data[11:]
    new_phenomenon = Phenomenon.query.filter_by(phenomenon=phenomenon_data, user_id=user_id).first()
    try:
        db.session.delete(new_phenomenon)
        text = hints['phenomenon delete'][lang]
    except:
        new_phenomenon = Phenomenon(phenomenon=phenomenon_data, user_id=user_id)
        db.session.add(new_phenomenon)
        text = hints['phenomenon set'][lang]

    db.session.commit()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=hints['phenomena intro'][lang], reply_markup=gen_markup_phenomena(user.id, lang))
    bot.answer_callback_query(
        callback_query_id=call.id, show_alert=False,
        text=f"{hints['phenomenon set del'][lang]} {inline_buttons[phenomenon_data][lang]} {text}")


# handle back to phenomenon button
@bot.callback_query_handler(func=lambda call: call.data == "back_to_ph")
def callback_inline_back_ph(call):
    user = User.query.filter_by(chat_id=call.message.chat.id).first()
    lang = user.language
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=hints['phenomena intro'][lang], reply_markup=gen_markup_phenomena(user.id, lang))


# handle daily inline keyboard (hours)
def gen_markup_daily(user_id):
    user = User.query.filter_by(id=user_id).first()
    markup = gen_markup_hours(user_id=user_id, model=ReminderTime, lang=user.language)
    reminders = ReminderTime.query.filter_by(minutes=None, user_id=user_id).all()
    for reminder in reminders:
        db.session.delete(reminder)
    db.session.commit()
    return markup


# handle daily inline keyboard (minutes)
@bot.callback_query_handler(func=lambda call: "hr" in call.data)
def callback_inline_daily_min(call):
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    user_id = user.id
    lang = user.language
    hours = call.data[:2]

    markup = gen_markup_minutes(user_id=user_id, hours=hours, model=ReminderTime, lang=lang)

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=hints['time daily'][lang], reply_markup=markup)


@bot.callback_query_handler(func=lambda call: 'min' in call.data)
def callback_inline_daily(call):
    """writing time to db"""
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    user_id = user.id
    lang = user.language

    reminder_hours = call.data[:2]
    reminder_minutes = call.data[3:5]
    existing_reminder = ReminderTime.query.filter_by(user_id=user_id, hours=reminder_hours,
                                                     minutes=reminder_minutes).first()
    if existing_reminder:  # if reminder exists
        sched.remove_job(job_id=existing_reminder.job_id)  # remove the time from schedule
        db.session.delete(existing_reminder)  # remove the time from db
        db.session.commit()
        text = f"{hints['schedule delete'][lang]}"
    else:  # if reminder does not exist
        new_reminder = ReminderTime(user_id=user_id, hours=reminder_hours, minutes=reminder_minutes)
        db.session.add(new_reminder)
        db.session.commit()
        set_daily(new_reminder, reminder_hours, reminder_minutes)
        text = f"{hints['schedule set'][lang]} {reminder_hours}:{reminder_minutes}"

    callback_inline_daily_min(call)
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=text)


# handle back to hours button
@bot.callback_query_handler(func=lambda call: call.data == "back_to_hours")
def callback_inline_back(call):
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    user_id = user.id

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=hints['time daily'][user.language],
                          reply_markup=gen_markup_daily(user_id))


@bot.callback_query_handler(func=lambda call: "remove all daily" in call.data)
def callback_remove_all_daily(call):
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    lang = user.language

    all_reminders = user.reminder_time
    for reminder in all_reminders:
        sched.remove_job(job_id=reminder.job_id)  # remove the time from schedule
        db.session.delete(reminder)  # remove the time from db
    db.session.commit()

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f"{hints['schedule delete'][lang]}", reply_markup=gen_markup_hours(
            user_id=user.id, model=ReminderTime, lang=lang))


# handle language button
@bot.callback_query_handler(func=lambda call: call.data == "english" or call.data == "russian")
def callback_inline_language(call):
    user = User.query.filter_by(chat_id=call.message.chat.id).first()
    new_lang = call.data[:2]
    user.language = new_lang
    db.session.commit()
    bot.send_message(chat_id=call.message.chat.id, text=f'{hints["lang chosen"][new_lang]}',
                     reply_markup=call_settings_keyboard(lang=new_lang))


if __name__ == '__main__':
    phenomenon_info(1)
