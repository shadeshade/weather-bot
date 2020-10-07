import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from flask import request
from sqlalchemy.orm.exc import UnmappedInstanceError
from telebot.apihelper import ApiException

from app import app, db, bot
from app.data.localization import buttons, inline_buttons, ph_info
from app.telegrambot.credentials import HEROKU_DEPLOY_DOMAIN, NGROK_DEPLOY_DOMAIN, TOKEN
from app.telegrambot.mastermind import *
from app.telegrambot.models import *
from app.telegrambot.settings import DEBUG
from app.telegrambot.tele_buttons import phenomena_list, gen_markup_minutes, gen_markup_hours, gen_markup_phenomena, \
    gen_markup_language, call_main_keyboard, call_settings_keyboard, gen_markup_phenomena_manually, \
    phenomena_manually_list

sched = BackgroundScheduler()


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    bot.remove_webhook()
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
    user_data = get_user_data(message)
    chat_id = user_data['chat_id']
    lang = user_data['lang']
    user = user_data['user']
    username = user_data['username']

    if not user:
        new_user = User(username=username, chat_id=chat_id, language=lang)
        db.session.add(new_user)
        db.session.commit()

    response = get_start(username, lang)
    bot.send_message(chat_id, text=response, reply_markup=call_main_keyboard(lang), parse_mode='html')


# Handle button 'weather now'
@bot.message_handler(
    func=lambda message: message.text == buttons['weather now']['en'] or message.text == buttons['weather now']['ru'])
def button_weather_now(message, ):
    user_data = get_user_data(message)
    chat_id = user_data['chat_id']
    lang = user_data['lang']
    user = user_data['user']
    city_name = user_data['city_name']

    if not user or not city_name:
        return bot.send_message(chat_id=chat_id, text=hints['no city'][lang], parse_mode='html')

    response = get_response(city_name, lang, message.date)
    bot.send_message(chat_id=chat_id, text=response, parse_mode='html')


# Handle button 'for tomorrow'
@bot.message_handler(
    func=lambda message: message.text == buttons['for tomorrow']['en'] or message.text == buttons['for tomorrow']['ru'])
def button_tomorrow(message, ):
    user_data = get_user_data(message)
    chat_id = user_data['chat_id']
    lang = user_data['lang']
    user = user_data['user']
    city_name = user_data['city_name']

    if not user or not city_name:
        return bot.send_message(chat_id=chat_id, text=hints['no city'][lang], parse_mode='html')

    response = get_next_day(city_name, lang, phenomenon_info=False)
    bot.send_message(chat_id=chat_id, text=response, parse_mode='html')


# Handle button 'for a week'
@bot.message_handler(
    func=lambda message: message.text == buttons['for a week']['en'] or message.text == buttons['for a week']['ru'])
def button_week(message, ):
    user_data = get_user_data(message)
    chat_id = user_data['chat_id']
    lang = user_data['lang']
    user = user_data['user']
    city_name = user_data['city_name']

    if not user or not city_name:
        return bot.send_message(chat_id=chat_id, text=hints['no city'][lang], parse_mode='html')

    response = get_next_week(city=city_name, lang=lang)
    bot.send_message(chat_id=chat_id, text=response, parse_mode='html')


# Handle button 'settings'
@bot.message_handler(
    func=lambda message: message.text == buttons['settings']['en'] or message.text == buttons['settings']['ru'])
def button_settings(message, ):
    user_data = get_user_data(message)
    chat_id = user_data['chat_id']
    lang = user_data['lang']

    bot.send_message(chat_id, text=info[lang][9], reply_markup=call_settings_keyboard(lang))


# Handle button 'daily'
@bot.message_handler(
    func=lambda message: message.text == buttons['daily']['en'] or message.text == buttons['daily']['ru'])
def button_daily(message):
    user_data = get_user_data(message)
    chat_id = user_data['chat_id']
    lang = user_data['lang']
    user = user_data['user']
    city_name = user_data['city_name']

    if not user or not city_name:
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
    # if hours is None or minutes is None:
    #     db.session.delete(new_reminder)
    #     db.session.commit()
    #     return
    job = sched.add_job(
        daily_info, args=[new_reminder.user_id, f'{hours}.{minutes}'], trigger='cron', hour=hours, minute=minutes
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


# Handle button 'phenomena'
@bot.message_handler(
    func=lambda message: message.text == buttons['phenomena']['en'] or message.text == buttons['phenomena']['ru'])
def button_phenomena(message, ):
    user_data = get_user_data(message)
    chat_id = user_data['chat_id']
    lang = user_data['lang']
    user = user_data['user']
    city_name = user_data['city_name']

    if not user or not city_name:
        return bot.send_message(chat_id, hints['no city'][lang])

    response = hints['phenomena intro'][lang]
    bot.send_message(chat_id, text=response, reply_markup=gen_markup_phenomena(user.id, lang))


# Handle phenomenon reminder
def set_phenomenon_time(new_reminder, hours, minutes):
    user_id = new_reminder.user_id
    job = sched.add_job(phenomenon_info, args=[user_id], trigger='cron', hour=hours, minute=minutes, )
    new_reminder.job_id = job.id
    db.session.commit()

    if sched.state == 0:
        sched.start()


# Handle phenomenon reminder (sending a reminder)
def phenomenon_info(user_id):
    user = User.query.filter_by(id=user_id).first()
    lang = user.language
    next_day_max_val = {'temp_positive': 0, 'temp_negative': 0, 'condition': [], 'wind': 0, 'humidity': 0}
    next_day_info = get_next_day(user.city_name, user.language, phenomenon_info=True)
    for day_part_info in next_day_info.values():
        if '+' in day_part_info['daypart_temp']:  # temp_positive
            temp_positive = int(day_part_info['daypart_temp'].split('+')[-1].replace('°', ''))
            if temp_positive > next_day_max_val['temp_positive']:
                next_day_max_val['temp_positive'] = temp_positive
        elif '-' in day_part_info['daypart_temp']:  # temp_negative
            daypart_temp_negative = int(day_part_info['daypart_temp'].split('-')[-1].replace('°', ''))
            if daypart_temp_negative > next_day_max_val['temp_negative']:
                next_day_max_val['temp_negative'] = daypart_temp_negative

        condition = day_part_info['daypart_condition']  # condition
        next_day_max_val['condition'] += [condition.lower()]

        wind = float(day_part_info['daypart_wind'].replace(',', '.'))  # wind
        if wind > next_day_max_val['wind']:
            next_day_max_val['wind'] = wind

        humidity = int(day_part_info['daypart_humidity'].replace('%', ''))  # humidity
        if humidity > next_day_max_val['humidity']:
            next_day_max_val['humidity'] = humidity

    temp_positive = next_day_max_val['temp_positive']
    temp_negative = next_day_max_val['temp_negative']
    condition = next_day_max_val['condition']
    wind = next_day_max_val['wind']
    humidity = next_day_max_val['humidity']

    text = ''
    all_phenomena = Phenomenon.query.filter_by(user_id=user.id).all()
    for phenomenon in all_phenomena:
        existing_ph = ph_info[phenomenon.phenomenon][lang]
        if existing_ph in condition:
            val_and_unit = condition
            pass
        elif existing_ph == ph_info["strong wind"][lang]:
            if 29 >= wind >= 12:
                val_and_unit = f'{wind} {info[lang][10]}'
                pass
            else:
                continue
        elif existing_ph == ph_info["hurricane"][lang]:
            if wind >= 30:
                val_and_unit = f'{wind} {info[lang][10]}'
                pass
            else:
                continue
        elif existing_ph == ph_info["intense heat"][lang]:
            if temp_positive >= 30:
                val_and_unit = f'+{temp_positive}°C'
                pass
            else:
                continue
        else:
            continue
        text += f'\n{existing_ph.capitalize()} {val_and_unit}'

    all_man_phenomena = PhenomenonManually.query.filter_by(user_id=user_id).all()
    for man_ph in all_man_phenomena:
        ph = ph_info[man_ph.phenomenon][lang]
        val = man_ph.value
        if ph == ph_info['positive temperature'][lang]:
            if val <= temp_positive:
                val_and_unit = f'+{temp_positive}°C'
                pass
            else:
                continue
        elif ph == ph_info['negative temperature'][lang]:
            if val <= temp_negative:
                val_and_unit = f'-{temp_negative}°C'
                pass
            else:
                continue
        elif ph == ph_info['wind speed'][lang]:
            if val <= wind:
                val_and_unit = f'{wind} {info[lang][10]}'
                pass
            else:
                continue
        elif ph == ph_info['humidity'][lang]:
            if val <= humidity:
                val_and_unit = f'{humidity}%'
                pass
            else:
                continue
        else:
            continue
        if ph == ph_info['positive temperature'][lang] or ph == ph_info['negative temperature'][lang]:
            ph = info[lang][11]
        text += f'\n{ph.capitalize()} {val_and_unit}'

    if text:
        response_msg = f'<b>{hints["phenomenon tomorrow"][user.language]}</b>'
        response_msg += text
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


# Handle button 'city'
@bot.message_handler(
    func=lambda message: message.text == buttons['city']['en'] or message.text == buttons['city']['ru'])
def button_city(message, intro=True):
    user_data = get_user_data(message)
    chat_id = user_data['chat_id']
    lang = user_data['lang']
    user = user_data['user']
    username = user_data['username']

    if not user:
        new_user = User(username=username, chat_id=chat_id, language=lang)
        db.session.add(new_user)
        db.session.commit()

    if intro:  # if button_city called first time
        text = hints['city intro'][lang]
    else:  # if user types incorrect city name
        text = info[lang][0]

    msg = bot.send_message(chat_id=chat_id, text=text)
    bot.register_next_step_handler(message=msg, callback=add_city)


# Handle button 'city'
def add_city(message):
    chat_id = message.chat.id
    user = User.query.filter_by(chat_id=chat_id).first()
    lang = user.language
    city = message.text

    btns = {value[lang] for key, value in buttons.items()}
    inline_btns = {value[lang] for key, value in inline_buttons.items()}
    if message.text in btns or message.text in inline_btns:
        return bot.send_message(chat_id, hints['cancel'][lang])

    response = get_response(city, lang, message.date)

    if info[lang][0] not in response:
        user.city_name = city
        db.session.commit()
        return bot.send_message(chat_id=chat_id, text=f"{hints['city added'][lang]}")
    else:
        bot.send_message(chat_id=chat_id, text=f"{hints['city fail'][lang]}")
        return button_city(message, intro=False)


# Handle button 'language'
@bot.message_handler(
    func=lambda message: message.text == buttons['language']['en'] or message.text == buttons['language']['ru'])
def button_language(message, ):
    user_data = get_user_data(message)
    chat_id = user_data['chat_id']
    lang = user_data['lang']
    user = user_data['user']
    username = user_data['username']

    if not user:
        new_user = User(username=username, chat_id=chat_id, language=lang)
        db.session.add(new_user)
        db.session.commit()

    response = hints['lang intro'][lang]
    bot.send_message(chat_id=chat_id, text=response, reply_markup=gen_markup_language(user_id=user.id))


# Handle button 'info'
@bot.message_handler(
    func=lambda message: message.text == buttons['info']['en'] or message.text == buttons['info']['ru'])
def button_info(message, ):
    user_data = get_user_data(message)
    user_id = user_data['user'].id
    lang = user_data['lang']
    all_phenomena = Phenomenon.query.filter_by(user_id=user_id).all()
    all_man_phenomena = PhenomenonManually.query.filter_by(user_id=user_id).all()
    all_daily = ReminderTime.query.filter_by(user_id=user_id).all()

    daily_text = ''
    for daily in all_daily:
        daily_text += f'{daily.hours}:{daily.minutes}\n'
    if not daily_text:
        daily_text = 'not set' + '\n'

    ph_text = ''
    for ph in all_phenomena:
        ph_text += f'{ph.phenomenon.capitalize()}\n'
    if not ph_text:
        ph_text = 'empty' + '\n'

    man_ph_text = ''
    for man_ph in all_man_phenomena:
        man_ph_text += f'{man_ph.phenomenon.capitalize()} - {man_ph.value}\n'
    if not man_ph_text:
        man_ph_text = 'empty' + '\n'

    daily_btn = buttons["daily"][lang]
    ph_btn = buttons["phenomena"][lang]
    man_ph_btn = inline_buttons["manually"][lang]
    ph_time = PhenomenonTime.query.filter_by(user_id=user_id).first()

    try:
        ph_time = f'{ph_time.hours}:{ph_time.minutes}'
    except AttributeError as e:
        logger.warning(f'Time was not set\n{repr(e)}')
        ph_time = 'not set'

    response = f'<b>{daily_btn}:</b>\n<b>Время:</b>\n{daily_text}' \
               f'\n<b>{ph_btn}:</b>\n{ph_text}' \
               f'\n<b>{man_ph_btn}:</b>\n{man_ph_text}' \
               f'\n<b>Время:</b>\n{ph_time}'
    bot.send_message(chat_id=message.chat.id, text=response, parse_mode='html')


# Handle button 'help'
@bot.message_handler(
    func=lambda message: message.text == buttons['help']['en'] or message.text == buttons['help']['ru'])
def button_help(message, ):
    user_data = get_user_data(message)
    chat_id = user_data['chat_id']
    lang = user_data['lang']

    response = get_help(lang)
    bot.send_message(chat_id, text=response, parse_mode='html')


# Handle button 'menu'
@bot.message_handler(
    func=lambda message: message.text == buttons['menu']['en'] or message.text == buttons['menu']['ru'])
def button_menu(message, ):
    user_data = get_user_data(message)
    chat_id = user_data['chat_id']
    lang = user_data['lang']

    bot.send_message(chat_id, text=hints['menu'][lang], reply_markup=call_main_keyboard(lang))


# Handle all other messages with content_type 'sticker' and 'text' (content_types defaults to ['text'])
@bot.message_handler(content_types=["sticker", "text"])
def respond(message):
    if message.sticker:
        sticker = open('app/static/AnimatedSticker.tgs', 'rb')
        return bot.send_sticker(message.chat.id, sticker)
    else:
        user_data = get_user_data(message)
        chat_id = user_data['chat_id']
        lang = user_data['lang']
        user = user_data['user']
        username = user_data['username']
        city_name = user_data['city_name']

        city = message.text
        response = get_response(city, lang, message.date)

        if 'Try again' not in response:
            if not user:
                user = User(username=username, chat_id=chat_id, city_name=city, language=lang)
                db.session.add(user)
                db.session.commit()
            elif not city_name:
                user.city_name = city
                db.session.commit()

        return bot.send_message(chat_id=chat_id, text=response, parse_mode='html')


# handle phenomenon inline keyboard time setting (hours)
@bot.callback_query_handler(func=lambda call: call.data == "back_to_hours_ph" or call.data == "set time phenomena")
def callback_phenomenon_time(call):
    """imported temp_buttons"""

    user = User.query.filter_by(chat_id=call.from_user.id).first()
    lang = user.language
    user_id = user.id

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

    phenomenon = PhenomenonTime.query.filter_by(
        user_id=user_id, hours=phenomenon_hours, minutes=phenomenon_minutes).first()

    delete_ph_time_jobs(user_id)
    ph_reminders = PhenomenonTime.query.filter_by(user_id=user_id).all()
    for reminder in ph_reminders:
        db.session.delete(reminder)
    db.session.commit()

    if phenomenon:
        text = f"{hints['schedule delete'][lang]}"
    else:
        new_phenomenon = PhenomenonTime(user_id=user_id, hours=phenomenon_hours, minutes=phenomenon_minutes)
        db.session.add(new_phenomenon)  # commits in set_phenomenon_time func
        set_phenomenon_time(new_phenomenon, new_phenomenon.hours, new_phenomenon.minutes)
        text = f"{hints['schedule set'][lang]} {phenomenon_hours}:{phenomenon_minutes}"


    callback_phenomenon_hr(call)
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=text)


# handle inline button 'manually'
@bot.callback_query_handler(func=lambda call: call.data == "phenomena manually")
def callback_button_manually(call):
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    user_id = user.id
    lang = user.language

    bot.edit_message_text(
        chat_id=call.message.chat.id, message_id=call.message.message_id, text=hints['phenomena manually intro'][lang],
        reply_markup=gen_markup_phenomena_manually(user_id, lang)
    )


# handle phenomenon manually db
@bot.callback_query_handler(func=lambda call: "manually" in call.data)
def callback_phenomenon_manually(call, intro=True):
    global callback_query_ph_manually
    callback_query_ph_manually = call
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    lang = user.language

    if intro:  # if callback_phenomenon_manually called first time
        text = f"{hints['phenomena temp set'][lang]}\n{hints['num expected'][lang]}"
    else:  # if user types incorrect msg
        text = info[lang][0]

    msg = bot.send_message(call.from_user.id, text)
    bot.register_next_step_handler(message=msg, callback=add_phenomenon_manually)


# handle phenomenon manually db
def add_phenomenon_manually(message):
    msg = message.text
    chat_id = message.chat.id
    user = User.query.filter_by(chat_id=chat_id).first()
    lang = user.language
    ph_data = callback_query_ph_manually.data[9:]
    phenomenon = PhenomenonManually.query.filter_by(phenomenon=ph_data, user_id=user.id).first()

    btns = {value[lang] for key, value in buttons.items()}
    inline_btns = {value[lang] for key, value in inline_buttons.items()}
    if msg in btns or msg in inline_btns:
        return bot.send_message(chat_id, hints['cancel'][lang])

    try:  # check if msg is not a num
        msg = int(msg)
    except:
        bot.send_message(chat_id, hints['num expected'][lang])
        return callback_phenomenon_manually(callback_query_ph_manually, intro=False)

    if msg == 0:  # delete phenomenon value
        try:
            db.session.delete(phenomenon)
        except UnmappedInstanceError as e:
            logger.error(f'The phenomenon has not been found.\n{e}')
        else:
            db.session.commit()
        finally:
            return bot.send_message(
                chat_id, f"{ph_data.capitalize()} {hints['phenomenon delete'][lang]}",
                reply_markup=gen_markup_phenomena_manually(user.id, lang))

    elif ph_data in phenomena_manually_list:  # if user enters a wrong number
        text = None
        if ph_data in phenomena_manually_list[0] or ph_data in phenomena_manually_list[2:]:
            if msg < 0:
                text = f"{hints['num pos expected'][lang]}"
        elif ph_data == 'negative temperature' and msg > 0:
            text = f"{hints['num neg expected'][lang]}"
        if text:
            bot.send_message(chat_id, text)
            return callback_phenomenon_manually(callback_query_ph_manually, intro=False)

    try:  # add value to db
        phenomenon.value = msg
    except AttributeError as e:
        logger.error(f'The phenomenon has not been found.\n{repr(e)}')
        new_phenomenon = PhenomenonManually(phenomenon=ph_data, value=msg, user_id=user.id)
        db.session.add(new_phenomenon)
    finally:
        db.session.commit()
        return bot.send_message(
            chat_id, f"{hints['phenomenon'][lang]} {ph_data} {hints['ph manually set'][lang]} {msg}",
            reply_markup=gen_markup_phenomena_manually(user.id, lang))


# handle all phenomena db
@bot.callback_query_handler(func=lambda call: call.data == "all phenomena")
def callback_all_phenomena(call):
    """"add all phenomena to db"""
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    user_id = user.id
    lang = user.language

    phenomena_data = Phenomenon.query.filter_by(user_id=user_id).all()
    if len(phenomena_data) > 6:
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
    phenomenon = Phenomenon.query.filter_by(phenomenon=phenomenon_data, user_id=user_id).first()

    try:
        db.session.delete(phenomenon)
    except UnmappedInstanceError as e:
        logger.error(f'The phenomenon has not been found. Creating new one\n{e}')
        new_phenomenon = Phenomenon(phenomenon=phenomenon_data, user_id=user_id)
        db.session.add(new_phenomenon)
        text = hints['phenomenon set'][lang]
    else:
        text = hints['phenomenon delete'][lang]

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
    # reminders = ReminderTime.query.filter_by(minutes=None, user_id=user_id).all()
    # for reminder in reminders:
    #     db.session.delete(reminder)
    # db.session.commit()
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

    bot.edit_message_text(
        chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{hints['schedule delete'][lang]}",
        reply_markup=gen_markup_hours(user_id=user.id, model=ReminderTime, lang=lang))


# Handle button 'language'
@bot.callback_query_handler(func=lambda call: call.data == "english" or call.data == "russian")
def callback_inline_language(call):
    user = User.query.filter_by(chat_id=call.message.chat.id).first()
    new_lang = call.data[:2]
    user.language = new_lang
    db.session.commit()

    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=hints['lang intro'][user.language],
                              reply_markup=gen_markup_language(user_id=user.id))
    except ApiException as e:  # bad request
        logger.warning(f'Bad request. The output message has not been changed\n({e})')
    else:
        bot.send_message(chat_id=call.message.chat.id, text=f'{hints["lang chosen"][new_lang]}',
                         reply_markup=call_settings_keyboard(lang=new_lang))


if __name__ == '__main__':
    phenomenon_info(1)
