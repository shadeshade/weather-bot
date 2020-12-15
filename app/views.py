import telebot
from flask import request
from sqlalchemy.orm.exc import UnmappedInstanceError
from telebot.apihelper import ApiException

from app import server, bot
from app.credentials import HEROKU_DEPLOY_DOMAIN, NGROK_DEPLOY_DOMAIN, TOKEN, DEBUG
from app.data.localization import button_names
from app.mastermind.formating import *
from app.mastermind.scheduling import delete_ph_time_jobs, set_phenomenon_time, set_daily, scheduler
from app.mastermind.tele_buttons import phenomena_list, gen_markup_minutes, gen_markup_hours, gen_markup_phenomena, \
    gen_markup_language, call_main_keyboard, call_settings_keyboard, gen_markup_phenomena_manually, \
    ph_manual_list
from app.models import *


def get_message_handler_func(button_key):
    return lambda message: message.text == button_names[button_key]['en'] or \
                           message.text == button_names[button_key]['ru']


def view_pre_process_actions(check_city_present=False):
    def decorator(function):
        def wrapper(message):
            data = User.get_or_create_user_data(message)
            if check_city_present and (not data['user'] or not data['city_name']):
                return bot.send_message(chat_id=data['chat_id'],
                                        text=hints['no city'][data['lang']],
                                        parse_mode='html')

            return function(message, data)

        return wrapper

    return decorator


@server.route('/setwebhook', methods=['GET'])
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


@server.route(f'/{TOKEN}', methods=['POST'])
def get_update():
    """handle incoming messages"""
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok", 200


@bot.message_handler(commands=['start'])
@view_pre_process_actions()
def command_start(message, data):
    """Handle '/start'"""
    response = get_start(data['username'], data['lang'])
    bot.send_message(data['chat_id'], text=response,
                     reply_markup=call_main_keyboard(data['lang']), parse_mode='html')


@bot.message_handler(func=get_message_handler_func('weather now'))
@view_pre_process_actions(check_city_present=True)
def button_weather_now(message, data):
    """Handle button 'weather now'"""
    response = get_today_weather_info(data['city_name'], data['lang'], message.date)
    bot.send_message(chat_id=data['chat_id'], text=response, parse_mode='html')


@bot.message_handler(func=get_message_handler_func('for tomorrow'))
@view_pre_process_actions(check_city_present=True)
def button_tomorrow(message, data):
    """Handle button 'for tomorrow'"""
    response = get_next_day(data['city_name'], data['lang'], phenomenon_info=False)
    bot.send_message(chat_id=data['chat_id'], text=response, parse_mode='html')


@bot.message_handler(func=get_message_handler_func('for a week'))
@view_pre_process_actions(check_city_present=True)
def button_week(message, data):
    """Handle button 'for a week'"""
    response = get_next_week(city=data['city_name'], lang=data['lang'])
    bot.send_message(chat_id=data['chat_id'], text=response, parse_mode='html')


@bot.message_handler(func=get_message_handler_func('settings'))
@view_pre_process_actions()
def button_settings(message, data):
    """Handle button 'settings'"""
    bot.send_message(data['chat_id'], text=info[data['lang']][9], reply_markup=call_settings_keyboard(data['lang']))


@bot.message_handler(func=get_message_handler_func('daily'))
@view_pre_process_actions(check_city_present=True)
def button_daily(message, data):
    """Handle button 'daily'"""
    reminders = Reminder.query.filter_by(is_phenomenon=False).all()
    for reminder in reminders:
        if reminder.hours is None or reminder.minutes is None:
            db.session.delete(reminder)
            db.session.commit()
    response = hints['time daily'][data['lang']]
    bot.send_message(data['chat_id'], text=response, reply_markup=gen_markup_daily(data['user'].id))


@bot.message_handler(func=get_message_handler_func('phenomena'))
@view_pre_process_actions(check_city_present=True)
def button_phenomena(message, data):
    """Handle button 'phenomena'"""
    response = hints['phenomena intro'][data['lang']]
    bot.send_message(data['chat_id'], text=response, reply_markup=gen_markup_phenomena(data['user'].id, data['lang']))


@bot.message_handler(func=get_message_handler_func('city'))
def button_city(message, intro=True):
    """Handle button 'city'"""
    data = User.get_or_create_user_data(message)

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


def add_city(message):
    """Handle button 'city'"""
    data = User.get_or_create_user_data(message)
    city = message.text

    btns = {value[data['lang']] for key, value in button_names.items()}
    inline_btns = {value[data['lang']] for key, value in phenomenon_button_names.items()}
    if message.text in btns or message.text in inline_btns:
        return bot.send_message(data['chat_id'], hints['cancel'][data['lang']])

    response = get_today_weather_info(city, data['lang'], message.date)

    if info[data['lang']][0] not in response:
        data['user'].city_name = city
        db.session.commit()
        return bot.send_message(chat_id=data['chat_id'], text=f"{hints['city added'][data['lang']]}")
    else:
        bot.send_message(chat_id=data['chat_id'], text=f"{hints['city fail'][data['lang']]}")
        return button_city(message, intro=False)


@bot.message_handler(func=get_message_handler_func('language'))
@view_pre_process_actions()
def button_language(message, data):
    """Handle button 'language'"""
    response = hints['lang intro'][data['lang']]
    bot.send_message(chat_id=data['chat_id'], text=response, reply_markup=gen_markup_language(user_id=data['user'].id))


@bot.message_handler(func=get_message_handler_func('info'))
@view_pre_process_actions(check_city_present=True)
def button_info(message, data):
    """Handle button 'info'"""
    all_phenomena = Phenomenon.query.filter_by(user_id=data['user'].id, is_manually=False).all()
    all_manual_phenomena = Phenomenon.query.filter_by(user_id=data['user'].id, is_manually=True).all()
    all_daily = Reminder.query.filter_by(user_id=data['user'].id, is_phenomenon=False).all()

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
        ph_text += f'{phenomenon_button_names[ph.phenomenon][data["lang"]]}\n'
    if not ph_text:
        ph_text = f"{info[data['lang']][13]}\n"

    man_ph_text = ''
    for man_ph in all_manual_phenomena:
        if man_ph.phenomenon == phenomenon_button_names['wind speed']['en'].lower():
            unit = f' {info[data["lang"]][10]}'  # m/s
        elif man_ph.phenomenon == phenomenon_button_names['humidity']['en'].lower():
            unit = '%'
        else:  # temperature
            unit = '°C'
        man_ph_text += f'{phenomenon_button_names[man_ph.phenomenon][data["lang"]]}: {man_ph.value}{unit}\n'
    if not man_ph_text:
        man_ph_text = f"{info[data['lang']][13]}\n"

    daily_btn = button_names["daily"][data['lang']]
    ph_btn = button_names["phenomena"][data['lang']]
    man_ph_btn = phenomenon_button_names["manually"][data['lang']]
    ph_time = Reminder.query.filter_by(user_id=data['user'].id, is_phenomenon=True).first()

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


@bot.message_handler(commands=['help'])
@bot.message_handler(func=get_message_handler_func('help'))
@view_pre_process_actions()
def button_help(message, data):
    """Handle button 'help'"""
    response = hints['help intro'][data['lang']]
    bot.send_message(data['chat_id'], text=response, parse_mode='html')


@bot.message_handler(func=get_message_handler_func('menu'))
@view_pre_process_actions()
def button_menu(message, data):
    """Handle button 'menu'"""
    bot.send_message(data['chat_id'], text=hints['menu'][data['lang']], reply_markup=call_main_keyboard(data['lang']))


@bot.message_handler(content_types=["sticker", "text"])
@view_pre_process_actions()
def respond(message, data):
    """Handle all other messages with content_type 'sticker' and 'text' (content_types defaults to ['text'])"""
    if message.sticker:
        sticker = open('app/static/AnimatedSticker.tgs', 'rb')
        return bot.send_sticker(message.chat.id, sticker)
    else:
        city = message.text
        response = get_today_weather_info(city, data['lang'], message.date)

        if 'Try again' in response:
            return bot.send_message(data['chat_id'], text=response,
                                    reply_markup=call_main_keyboard(data['lang']))
        else:
            if not data['city_name']:
                data['user'].city_name = city
                db.session.commit()

        return bot.send_message(chat_id=data['chat_id'], text=response, parse_mode='html')


@bot.callback_query_handler(func=lambda call: call.data == "back_to_hours_ph" or call.data == "set time phenomena")
def callback_phenomenon_time(call):
    """handle phenomenon inline keyboard time setting (hours)"""
    user = User.query.filter_by(chat_id=call.from_user.id).first()

    markup = gen_markup_hours(user_id=user.id, is_phenomenon=True, lang=user.language, callback='_ph')
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=hints['phenomena time'][user.language], reply_markup=markup)


@bot.callback_query_handler(func=lambda call: 'hr_ph' in call.data)
def callback_phenomenon_hr(call):
    """handle phenomenon inline keyboard time setting (minutes)"""
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    hours = call.data[:2]

    markup = gen_markup_minutes(user_id=user.id, hours=hours, is_phenomenon=True, callback='_ph', lang=user.language)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=hints['phenomena time'][user.language], reply_markup=markup)


@bot.callback_query_handler(func=lambda call: 'min_ph' in call.data)
def callback_phenomenon_min(call):
    """
    handle phenomenon inline keyboard
    writing phenomenon time to db
    """
    user = User.query.filter_by(chat_id=call.from_user.id).first()

    phenomenon_hours = call.data[:2]
    phenomenon_minutes = call.data[3:5]

    phenomenon = Reminder.query.filter_by(
        user_id=user.id, hours=phenomenon_hours, minutes=phenomenon_minutes, is_phenomenon=True).first()

    delete_ph_time_jobs(user.id)
    ph_reminders = Reminder.query.filter_by(user_id=user.id, is_phenomenon=True).all()
    for reminder in ph_reminders:
        db.session.delete(reminder)
    db.session.commit()

    if phenomenon:
        text = f"{hints['schedule delete'][user.language]}"
    else:
        new_phenomenon = Reminder(user_id=user.id, hours=phenomenon_hours, minutes=phenomenon_minutes,
                                  is_phenomenon=True)
        db.session.add(new_phenomenon)  # commits in set_phenomenon_time func
        set_phenomenon_time(new_phenomenon, new_phenomenon.hours, new_phenomenon.minutes)
        text = f"{hints['schedule set'][user.language]} {phenomenon_hours}:{phenomenon_minutes}"

    callback_phenomenon_hr(call)
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=text)


@bot.callback_query_handler(func=lambda call: call.data == "phenomena manually")
def callback_button_manually(call):
    """handle inline button 'manually'"""
    user = User.query.filter_by(chat_id=call.from_user.id).first()

    bot.edit_message_text(
        chat_id=call.message.chat.id, message_id=call.message.message_id,
        text=hints['phenomena manually intro'][user.language],
        reply_markup=gen_markup_phenomena_manually(user.id, user.language)
    )


@bot.callback_query_handler(
    func=lambda call: ("manually" in call.data and call.data != "manually remove all" and call.data != "manually back"))
def callback_phenomenon_manually(call, intro=True):
    """handle phenomenon manually db"""
    global callback_query_ph_manually
    callback_query_ph_manually = call

    user = User.query.filter_by(chat_id=call.from_user.id).first()

    if intro:  # if callback_phenomenon_manually called first time
        text = f"{hints['phenomena temp set'][user.language]}\n{hints['num expected'][user.language]}" \
               f"\n{hints['how to del'][user.language]}"
    else:  # if user types incorrect msg
        text = info[user.language][0]

    msg = bot.send_message(call.from_user.id, text)
    bot.register_next_step_handler(message=msg, callback=add_phenomenon_manually)


def add_phenomenon_manually(message):
    """handle phenomenon manually db"""
    data = User.get_or_create_user_data(message)
    msg = message.text
    chat_id = data['chat_id']
    user = data['user']
    lang = data['lang']
    ph_data = callback_query_ph_manually.data[9:]
    phenomenon = Phenomenon.query.filter_by(phenomenon=ph_data, user_id=user.id, is_manually=True).first()

    btns = {value[lang] for key, value in button_names.items()}

    if msg in btns:
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
                chat_id,
                f'{hints["phenomenon"][lang]} "{phenomenon_button_names[ph_data][lang]}" {hints["phenomenon delete"][lang]}',
                reply_markup=gen_markup_phenomena_manually(user.id, lang))

    elif ph_data in ph_manual_list:  # if user enters a wrong number
        text = None
        if ph_data in ph_manual_list[2:]:
            if msg < 0:
                text = f"{hints['num pos expected'][lang]}"
        if text:
            bot.send_message(chat_id, text)
            return callback_phenomenon_manually(callback_query_ph_manually, intro=False)

    try:  # add value to db
        phenomenon.value = msg
    except AttributeError as e:
        logger.error(f'The phenomenon has not been found.\n{repr(e)}')
        new_phenomenon = Phenomenon(phenomenon=ph_data, value=msg, user_id=user.id, is_manually=True)
        db.session.add(new_phenomenon)
    finally:
        db.session.commit()
        return bot.send_message(
            chat_id,
            f'{hints["phenomenon"][lang]} "{phenomenon_button_names[ph_data][lang]}" {hints["ph manually set"][lang]} {msg}',
            reply_markup=gen_markup_phenomena_manually(user.id, lang))


@bot.callback_query_handler(func=lambda call: call.data == "manually remove all")
def callback_all_manual_phenomena(call):
    """handle all manually phenomena db
    add a manual phenomena to db"""
    user = User.query.filter_by(chat_id=call.from_user.id).first()

    manual_phenomena_from_db = Phenomenon.query.filter_by(user_id=user.id, is_manually=True).all()
    for ph in manual_phenomena_from_db:
        db.session.delete(ph)
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
            callback_query_id=call.id, show_alert=False,
            text=f"{hints['remove manually'][user.language]}")


@bot.callback_query_handler(func=lambda call: call.data == "manually back")
def callback_back_manually_phenomena(call):
    """
    handle all manually phenomena db
    add all man phenomena to db
    """
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=hints['phenomena intro'][user.language],
                          reply_markup=gen_markup_phenomena(
                              user.id, user.language))


@bot.callback_query_handler(func=lambda call: call.data == "all phenomena")
def callback_all_phenomena(call):
    """
    handle inline button 'all phenomena'
    add all phenomena to db
    """
    user = User.query.filter_by(chat_id=call.from_user.id).first()

    all_ph_from_db = Phenomenon.query.filter_by(user_id=user.id, value=None).all()
    if len(all_ph_from_db) == 7:
        for ph in all_ph_from_db:
            db.session.delete(ph)
        text = hints['all untick'][user.language]
    else:
        for ph in phenomena_list:
            new_phenomenon = Phenomenon.query.filter_by(phenomenon=ph, user_id=user.id).first()
            if new_phenomenon is None:
                new_phenomenon = Phenomenon(user_id=user.id, phenomenon=ph)
                db.session.add(new_phenomenon)
        text = hints['all tick'][user.language]
    db.session.commit()

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=hints['phenomena intro'][user.language],
                          reply_markup=gen_markup_phenomena(user.id, user.language))
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=text)


@bot.callback_query_handler(func=lambda call: 'phenomenon' in call.data)
def callback_phenomenon(call):
    """
    handle phenomenon db
    add phenomenon to db
    """
    user = User.query.filter_by(chat_id=call.from_user.id).first()

    phenomenon_data = call.data[11:]
    phenomenon = Phenomenon.query.filter_by(phenomenon=phenomenon_data, user_id=user.id).first()

    try:
        db.session.delete(phenomenon)
    except UnmappedInstanceError as e:
        logger.error(f'The phenomenon has not been found. Creating new one\n{e}')
        new_phenomenon = Phenomenon(phenomenon=phenomenon_data, user_id=user.id)
        db.session.add(new_phenomenon)
        text = hints['phenomenon set'][user.language]
    else:
        text = hints['phenomenon delete'][user.language]

    db.session.commit()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=hints['phenomena intro'][user.language],
                          reply_markup=gen_markup_phenomena(user.id, user.language))
    bot.answer_callback_query(
        callback_query_id=call.id, show_alert=False,
        text=f"{hints['phenomenon set del'][user.language]} "
             f"{phenomenon_button_names[phenomenon_data][user.language]} {text}")


@bot.callback_query_handler(func=lambda call: call.data == "back_to_ph")
def callback_inline_back_ph(call):
    """handle back to phenomenon button"""
    user = User.query.filter_by(chat_id=call.message.chat.id).first()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=hints['phenomena intro'][user.language],
                          reply_markup=gen_markup_phenomena(user.id, user.language))


def gen_markup_daily(user_id):
    """handle daily inline keyboard (hours)"""
    user = User.query.filter_by(id=user_id).first()
    markup = gen_markup_hours(user_id=user_id, is_phenomenon=False, lang=user.language)
    return markup


@bot.callback_query_handler(func=lambda call: "hr" in call.data)
def callback_inline_daily_min(call):
    """handle daily inline keyboard (minutes)"""
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    hours = call.data[:2]

    markup = gen_markup_minutes(user_id=user.id, hours=hours, is_phenomenon=False, lang=user.language)

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
    existing_reminder = Reminder.query.filter_by(
        user_id=user_id, hours=reminder_hours, minutes=reminder_minutes, is_phenomenon=False).first()
    if existing_reminder:  # if reminder exists
        scheduler.remove_job(job_id=existing_reminder.job_id, jobstore='default')  # remove the time from schedule
        db.session.delete(existing_reminder)  # remove the time from db
        db.session.commit()
        text = f"{hints['schedule delete'][lang]}"
    else:  # if reminder does not exist
        new_reminder = Reminder(
            user_id=user_id, hours=reminder_hours, minutes=reminder_minutes, is_phenomenon=False)
        db.session.add(new_reminder)
        db.session.commit()
        set_daily(new_reminder, reminder_hours, reminder_minutes)
        text = f"{hints['schedule set'][lang]} {reminder_hours}:{reminder_minutes}"

    callback_inline_daily_min(call)
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=text)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_hours")
def callback_inline_back(call):
    """handle back to hours button"""
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    user_id = user.id

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=hints['time daily'][user.language],
                          reply_markup=gen_markup_daily(user_id))


@bot.callback_query_handler(func=lambda call: call.data == "daily remove all")
def callback_remove_all_daily(call):
    user = User.query.filter_by(chat_id=call.from_user.id).first()
    all_reminders = Reminder.query.filter_by(user_id=user.id, is_phenomenon=False).all()

    for reminder in all_reminders:
        scheduler.remove_job(job_id=reminder.job_id, jobstore='default')  # remove the time from schedule
        db.session.delete(reminder)  # remove the time from db
    db.session.commit()
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"{hints['time daily'][user.language]}",
            reply_markup=gen_markup_hours(user_id=user.id, is_phenomenon=False, lang=user.language))
    except:
        pass
    finally:
        bot.answer_callback_query(
            callback_query_id=call.id, show_alert=False, text=f"{hints['schedule delete'][user.language]}")


@bot.callback_query_handler(func=lambda call: call.data == "english" or call.data == "russian")
def callback_inline_language(call):
    """Handle button 'language'"""
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
