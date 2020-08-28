import logging
from time import sleep

import telebot
from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.schedulers.base import STATE_STOPPED, STATE_RUNNING
from flask import request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from app import server, db, bot
from app.telegrambot.credentials import HEROKU_DEPLOY_DOMAIN, NGROK_DEPLOY_DOMAIN, TOKEN
from app.telegrambot.mastermind import *
from app.telegrambot.models import User, ReminderTime
from app.telegrambot.settings import DEBUG

sched = BackgroundScheduler()


# logging.basicConfig(level=logging.INFO)


# logging.basicConfig(filename='log.log',
#                     level=logging.INFO,
#                     filemode='w')
# telebot.logger.setLevel(logging.INFO)


@server.route('/setwebhook', methods=['GET', 'POST'])
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
@server.route(f'/{TOKEN}', methods=['POST'])
def get_update():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "", 200


# Handle '/start'
@bot.message_handler(commands=['start'])
def command_start(message, ):
    response = get_start(message.from_user.first_name)
    return bot.send_message(message.chat.id, text=response, reply_markup=call_main_keyboard(), parse_mode='html')


# Handle '/help'
@bot.message_handler(func=lambda message: message.text == '⁉ Помощь')
@bot.message_handler(commands=['help'])
def command_help(message, ):
    response = get_help()
    return bot.send_message(message.chat.id, text=response, )


# Handle '/daily'
@bot.message_handler(func=lambda message: message.text == '🌅 По графику')
@bot.message_handler(commands=['daily'])
def command_daily(message):
    if not bool(User.query.filter_by(chat_id=message.chat.id).first()):
        return bot.send_message(message.chat.id, text='No city name was set up', )
    # set_daily(message.chat.id)
    response = 'Set the time'
    return bot.send_message(message.chat.id, text=response, reply_markup=gen_markup())


# Handle '/daily' (setting a daily reminder)
def set_daily(user_id):
    # sched.remove_all_jobs()
    # sched.add_job(daily_info, trigger='interval', seconds=5, args=[chat_id])
    user = User.query.filter_by(id=user_id).first()
    hours = user.reminder_time[-1].hours
    minutes = user.reminder_time[-1].minutes
    sched.add_job(daily_info, trigger='cron', hour=hours, minute=minutes, args=[user_id])
    print(sched.state)
    if sched.state == 0:
        sched.start()


# Handle '/daily' (sending a reminder)
def daily_info(user_id):
    user = User.query.filter_by(id=user_id).first()
    city_name = user.city_name
    response = get_daily(city_name)
    return bot.send_message(user.chat_id, text=response, )


# Handle all other messages with content_type 'sticker' and 'text' (content_types defaults to ['text'])
@bot.message_handler(content_types=["sticker", "text"])
def respond(message):
    if message.text == 'Погода':
        cur_user = User.query.filter_by(chat_id=message.chat.id).first()
        try:
            response = get_response(cur_user.city_name)
        except:
            response = 'Write down your location'
        bot.send_message(chat_id=message.chat.id, text=response, )
        return 'ok', 200
    elif message.sticker:
        sticker = open('static/AnimatedSticker.tgs', 'rb')
        bot.send_sticker(message.chat.id, sticker)
        return 'ok', 200
    else:
        response = get_response(message.text)
        if 'Try again' not in response:
            if not bool(User.query.filter_by(chat_id=message.chat.id).first()):
                new_user = User(username=message.from_user.first_name, chat_id=message.chat.id, city_name=message.text)
                db.session.add(new_user)
                db.session.commit()
    bot.send_message(chat_id=message.chat.id, text=response, )
    return 'ok', 200


# handle main keyboard
def call_main_keyboard():
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn1 = KeyboardButton('Погода')
    btn2 = KeyboardButton('⁉ Помощь')
    btn3 = KeyboardButton('🌅 По графику')
    keyboard.add(btn1, btn2, )
    keyboard.add(btn3)
    return keyboard


# handle daily inline keyboard (hours)
def gen_markup():
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


# handle daily inline keyboard (minutes)
@bot.callback_query_handler(func=lambda call: "hr" in call.data)
def callback_inline(call):
    """
    writing hours data to db and changing keyboard
    """
    user_id = User.query.filter_by(chat_id=call.from_user.id).first()
    user_id = user_id.id

    reminder_hours = call.data[:-2]
    new_reminder = ReminderTime(hours=reminder_hours, user_id=user_id)
    db.session.add(new_reminder)
    db.session.commit()

    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(InlineKeyboardButton("✖00:00", callback_data="0min"),
               InlineKeyboardButton("✖00:10", callback_data="10min"),
               InlineKeyboardButton("✖00:20", callback_data="20min"),
               InlineKeyboardButton("✖00:30", callback_data="30min"),
               InlineKeyboardButton("✖00:40", callback_data="40min"),
               InlineKeyboardButton("✖00:50", callback_data="50min"),
               InlineKeyboardButton("Back", callback_data="back_to_hours"),
               )

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Set the time",
                          reply_markup=markup)


# handle daily inline keyboard
@bot.callback_query_handler(func=lambda call: 'min' in call.data)
def callback_inline(call):
    """
    writing minutes data to db and removing keyboard
    """
    user_id = User.query.filter_by(chat_id=call.from_user.id).first()
    user_id = user_id.id

    reminder_minutes = call.data[:-3]
    reminder = ReminderTime.query.filter_by(user_id=user_id, minutes=None).first()
    reminder.minutes = reminder_minutes
    db.session.add(reminder)
    db.session.commit()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Schedule was set up", reply_markup=None)  # remove inline buttons
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="ЭТО ТЕСТОВОЕ УВЕДОМЛЕНИЕ!!11")
    set_daily(user_id)


# handle back button
@bot.callback_query_handler(func=lambda call: call.data == "back_to_hours")
def callback_inline(call):
    if call.data == "back_to_hours":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="menu",
                              reply_markup=gen_markup())
