import telebot
from flask import request
from sqlalchemy.orm.exc import UnmappedInstanceError
from telebot.apihelper import ApiException

from app import app, bot
from app.credentials import HEROKU_DEPLOY_DOMAIN, NGROK_DEPLOY_DOMAIN, TOKEN, DEBUG
from app.data.localization import button_names, inline_button_names
from app.mastermind.formating import *
from app.mastermind.scheduling import delete_ph_time_jobs, set_phenomenon_time, set_daily, sched
from app.mastermind.tele_buttons import phenomena_list, gen_markup_minutes, gen_markup_hours, gen_markup_phenomena, \
    gen_markup_language, call_main_keyboard, call_settings_keyboard, gen_markup_phenomena_manually, \
    ph_manual_list
from app.models import *


@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    bot.remove_webhook()
    if DEBUG:
        res = bot.set_webhook(f'{NGROK_DEPLOY_DOMAIN}/{TOKEN}')
    else:
        res = bot.set_webhook(f'{HEROKU_DEPLOY_DOMAIN}/{TOKEN}')

    if res:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route(f'/{TOKEN}', methods=['POST'])
def get_update():
    """handle incoming messages"""
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok", 200


@bot.message_handler(commands=['start'])
def command_start(message, ):
    """Handle '/start'"""
    data = User.get_user_data(message)
    if not data['user']:
        new_user = User(username=data['username'], chat_id=data['chat_id'], language=data['lang'])
        db.session.add(new_user)
        db.session.commit()

    response = get_start(data['username'], data['lang'])
    bot.send_message(data['chat_id'], text=response,
                     reply_markup=call_main_keyboard(data['lang']), parse_mode='html')


def get_message_handler_func(button_key):
    return lambda message: message.text == button_names[button_key]['en'] or \
                           message.text == button_names[button_key]['ru']


@bot.message_handler(func=get_message_handler_func('weather now'))
def button_weather_now(message, ):
    """Handle button 'weather now'"""
    data = User.get_user_data(message)

    if not data['user'] or not data['city_name']:
        return bot.send_message(chat_id=data['chat_id'], text=hints['no city'][data['lang']], parse_mode='html')

    response = get_response(data['city_name'], data['lang'], message.date)
    bot.send_message(chat_id=data['chat_id'], text=response, parse_mode='html')


@bot.message_handler(func=get_message_handler_func('for tomorrow'))
def button_tomorrow(message, ):
    """Handle button 'for tomorrow'"""
    data = User.get_user_data(message)

    if not data['user'] or not data['city_name']:
        return bot.send_message(chat_id=data['chat_id'], text=hints['no city'][data['lang']], parse_mode='html')

    response = get_next_day(data['city_name'], data['lang'], phenomenon_info=False)
    bot.send_message(chat_id=data['chat_id'], text=response, parse_mode='html')


@bot.message_handler(func=get_message_handler_func('for a week'))
def button_week(message, ):
    """Handle button 'for a week'"""
    data = User.get_user_data(message)

    if not data['user'] or not data['city_name']:
        return bot.send_message(chat_id=data['chat_id'], text=hints['no city'][data['lang']], parse_mode='html')

    response = get_next_week(city=data['city_name'], lang=data['lang'])
    bot.send_message(chat_id=data['chat_id'], text=response, parse_mode='html')


@bot.message_handler(func=get_message_handler_func('settings'))
def button_settings(message, ):
    """Handle button 'settings'"""
    data = User.get_user_data(message)
    bot.send_message(data['chat_id'], text=info[data['lang']][9], reply_markup=call_settings_keyboard(data['lang']))


@bot.message_handler(func=get_message_handler_func('daily'))
def button_daily(message):
    """Handle button 'daily'"""
    data = User.get_user_data(message)

    if not data['user'] or not data['city_name']:
        return bot.send_message(data['chat_id'], hints['no city'][data['lang']])

    reminders = ReminderTime.query.all()
    for reminder in reminders:
        if reminder.hours is None or reminder.minutes is None:
            db.session.delete(reminder)
            db.session.commit()
    response = hints['time daily'][data['lang']]
    bot.send_message(data['chat_id'], text=response, reply_markup=gen_markup_daily(data['user'].id))


# TODO: in every view move a comment like that in docstring
# Handle button 'phenomena'
@bot.message_handler(func=get_message_handler_func('phenomena'))
def button_phenomena(message, ):
    data = User.get_user_data(message)

    if not data['user'] or not data['city_name']:
        return bot.send_message(data['chat_id'], hints['no city'][data['lang']])

    response = hints['phenomena intro'][data['lang']]
    bot.send_message(data['chat_id'], text=response, reply_markup=gen_markup_phenomena(data['user'].id, data['lang']))


@bot.message_handler(func=get_message_handler_func('city'))
def button_city(message, intro=True):
    """Handle button 'city'"""
    data = User.get_user_data(message)

    if not data['user']:
        new_user = User(username=data['username'], chat_id=data['chat_id'], language=data['lang'])
        db.session.add(new_user)
        db.session.commit()

    if intro:  # if button_city called first time
        text = hints['city intro'][data['lang']]
    else:  # if user types incorrect city name
        text = info[data['lang']][0]

    msg = bot.send_message(chat_id=data['chat_id'], text=text)
    bot.register_next_step_handler(message=msg, callback=add_city)


# Handle button 'city'
def add_city(message):
    chat_id = message.chat.id
    user = User.query.filter_by(chat_id=chat_id).first()
    lang = user.language
    city = message.text

    btns = {value[lang] for key, value in button_names.items()}
    inline_btns = {value[lang] for key, value in inline_button_names.items()}
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
@bot.message_handler(func=get_message_handler_func('language'))
def button_language(message, ):
    data = User.get_user_data(message)

    if not data['user']:
        new_user = User(username=data['username'], chat_id=data['chat_id'], language=data['lang'])
        db.session.add(new_user)
        db.session.commit()

    response = hints['lang intro'][data['lang']]
    bot.send_message(chat_id=data['chat_id'], text=response, reply_markup=gen_markup_language(user_id=data['user'].id))


# Handle button 'info'
@bot.message_handler(func=get_message_handler_func('info'))
def button_info(message, ):

    data = User.get_user_data(message)
    selected_phenomena = Phenomenon.query.filter_by(user_id=data['user'].id).all()
    all_phenomena = [ph for ph in selected_phenomena if ph.phenomenon in phenomena_list]
    all_manual_phenomena = [ph for ph in selected_phenomena if ph.phenomenon in ph_manual_list]
    all_daily = ReminderTime.query.filter_by(user_id=data['user'].id).all()

    daily_text = ''
    for daily in all_daily:
        hours = daily.hours
        minutes = daily.minutes
        if len(str(hours)) == 1:
            hours = f'{0}{hours}'
        if minutes == 0:
            minutes = '00'
        daily_text += f'{hours}:{minutes}\n'
    if not daily_text:
        daily_text = f"{info[data['lang']][13]}\n"

    ph_text = ''
    for ph in all_phenomena:
        ph_text += f'{ph_info[ph.phenomenon][data["lang"]]}\n'
    if not ph_text:
        ph_text = f"{info[data['lang']][13]}\n"

    man_ph_text = ''
    for man_ph in all_manual_phenomena:
        if man_ph.phenomenon == ph_info['wind speed']['en'].lower():
            unit = f' {info[data["lang"]][10]}'  # m/s
        elif man_ph.phenomenon == ph_info['humidity']['en'].lower():
            unit = '%'
        else:  # temperature
            unit = '°C'
        man_ph_text += f'{ph_info[man_ph.phenomenon][data["lang"]]}: {man_ph.value}{unit}\n'
    if not man_ph_text:
        man_ph_text = f"{info[data['lang']][13]}\n"

    daily_btn = button_names["daily"][data['lang']]
    ph_btn = button_names["phenomena"][data['lang']]
    man_ph_btn = inline_button_names["manually"][data['lang']]
    ph_time = PhenomenonTime.query.filter_by(user_id=data['user'].id).first()

    try:
        hours = ph_time.hours
        minutes = ph_time.minutes
        if len(str(hours)) == 1:
            hours = f'{0}{hours}'
        if minutes == 0:
            minutes = '00'
        ph_time = f'{hours}:{minutes}'
    except AttributeError as e:
        logger.warning(f'Time was not set\n{repr(e)}')
        ph_time = f"{info[data['lang']][13]}\n"

    response = f'<b>{daily_btn}:</b>\n<b>{info[data["lang"]][12]}:</b>\n{daily_text}' \
               f'\n<b>{ph_btn}:</b>\n{ph_text}' \
               f'\n<b>{man_ph_btn}:</b>\n{man_ph_text}' \
               f'\n<b>{info[data["lang"]][12]}:</b>\n{ph_time}'
    bot.send_message(chat_id=message.chat.id, text=response, parse_mode='html')


# Handle button 'help'
@bot.message_handler(func=get_message_handler_func('help'))
def button_help(message, ):
    data = User.get_user_data(message)

    response = hints['help intro'][data['lang']]
    bot.send_message(data['chat_id'], text=response, parse_mode='html')


# Handle button 'menu'
@bot.message_handler(func=get_message_handler_func('menu'))
def button_menu(message, ):
    data = User.get_user_data(message)

    bot.send_message(data['chat_id'], text=hints['menu'][data['lang']], reply_markup=call_main_keyboard(data['lang']))


# Handle all other messages with content_type 'sticker' and 'text' (content_types defaults to ['text'])
@bot.message_handler(content_types=["sticker", "text"])
def respond(message):
    if message.sticker:
        sticker = open('app/static/AnimatedSticker.tgs', 'rb')
        return bot.send_sticker(message.chat.id, sticker)
    else:
        data = User.get_user_data(message)

        city = message.text
        response = get_response(city, data['lang'], message.date)

        if 'Try again' not in response:
            if not data['user']:
                data['user'] = User(username=data['username'], chat_id=data['chat_id'], city_name=city,
                                    language=data['lang'])
                db.session.add(data['user'])
                db.session.commit()
            elif not data['city_name']:
                data['user'].city_name = city
                db.session.commit()

        return bot.send_message(chat_id=data['chat_id'], text=response, parse_mode='html')


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
@bot.callback_query_handler(
    func=lambda call: ("manually" in call.data and call.data != "manually remove all" and call.data != "manually back"))
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
    phenomenon = Phenomenon.query.filter_by(phenomenon=ph_data, user_id=user.id).first()

    btns = {value[lang] for key, value in button_names.items()}
    inline_btns = {value[lang] for key, value in inline_button_names.items()}
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

    elif ph_data in ph_manual_list:  # if user enters a wrong number
        text = None
        if ph_data in ph_manual_list[0] or ph_data in ph_manual_list[2:]:
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
        new_phenomenon = Phenomenon(phenomenon=ph_data, value=msg, user_id=user.id)
        db.session.add(new_phenomenon)
    finally:
        db.session.commit()
        return bot.send_message(
            chat_id, f"{hints['phenomenon'][lang]} {ph_data} {hints['ph manually set'][lang]} {msg}",
            reply_markup=gen_markup_phenomena_manually(user.id, lang))


# handle all manually phenomena db
@bot.callback_query_handler(func=lambda call: call.data == "manually remove all")
def callback_all_manually_phenomena(call):
    """add all man phenomena to db"""
    user = User.query.filter_by(chat_id=call.from_user.id).first()

    all_ph_from_db = Phenomenon.query.filter_by(user_id=user.id).all()
    all_ph_from_db = [ph for ph in all_ph_from_db if ph.phenomenon in ph_manual_list]
    for ph in all_ph_from_db:
        db.session.delete(ph)
    text = hints['all untick'][user.language]
    db.session.commit()

    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text=hints['phenomena manually intro'][user.language],
            reply_markup=gen_markup_phenomena_manually(user.id, user.language))
    except:
        pass
    finally:
        bot.answer_callback_query(
            callback_query_id=call.id, show_alert=False, text=f"{hints['remove manually'][user.language]}")


# handle all manually phenomena db
@bot.callback_query_handler(func=lambda call: call.data == "manually back")
def callback_back_manually_phenomena(call):
    """add all man phenomena to db"""
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    user_id = user.id
    lang = user.language
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=hints['phenomena intro'][lang], reply_markup=gen_markup_phenomena(user.id, lang))


# handle inline button 'all phenomena'
@bot.callback_query_handler(func=lambda call: call.data == "all phenomena")
def callback_all_phenomena(call):
    """add all phenomena to db"""
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    user_id = user.id
    lang = user.language

    all_ph_from_db = Phenomenon.query.filter_by(user_id=user_id).all()
    if len(all_ph_from_db) == 7:
        for ph in all_ph_from_db:
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
        text=f"{hints['phenomenon set del'][lang]} {inline_button_names[phenomenon_data][lang]} {text}")


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
    return markup


# handle daily inline keyboard (minutes)
@bot.callback_query_handler(func=lambda call: "hr" in call.data)
def callback_inline_daily_min(call):
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    hours = call.data[:2]

    markup = gen_markup_minutes(user_id=user.id, hours=hours, model=ReminderTime, lang=user.language)

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=hints['time daily'][user.language], reply_markup=markup)


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


@bot.callback_query_handler(func=lambda call: call.data == "daily remove all")
def callback_remove_all_daily(call):
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    lang = user.language

    all_reminders = user.reminder_time
    for reminder in all_reminders:
        sched.remove_job(job_id=reminder.job_id)  # remove the time from schedule
        db.session.delete(reminder)  # remove the time from db
    db.session.commit()
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{hints['time daily'][lang]}",
            reply_markup=gen_markup_hours(user_id=user.id, model=ReminderTime, lang=lang))
    except:
        pass
    finally:
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=f"{hints['schedule delete'][lang]}")


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
