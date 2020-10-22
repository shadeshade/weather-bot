from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup

from app.data.localization import inline_buttons, buttons
from app.telegrambot.models import Phenomenon, User, PhenomenonManually

temp_buttons = ['temp_btn1', 'temp_btn2', 'temp_btn3', 'temp_btn4']
phenomena_list = ["strong wind", "hailstorm", "hurricane", "thunderstorm", "rain", "heavy rain", "intense heat"]


def get_main_keyboard_btns(lang, settings=False):
    """genarate button list for main keyboard"""
    main_keyboard_buttons = ['weather now', 'for tomorrow', 'for a week', 'settings', 'daily', 'phenomena', 'city',
                             'language', 'info', 'help', 'menu']
    button_list = []
    for idx in range(len(main_keyboard_buttons)):
        btn = KeyboardButton(buttons[main_keyboard_buttons[idx]][lang])
        button_list.append(btn)
    result = []
    if not settings:
        for idx in range(4):
            result.append(button_list[idx])
    else:
        for idx in range(4, 11):
            result.append(button_list[idx])
    return result


def call_main_keyboard(lang):
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btns = get_main_keyboard_btns(lang)
    keyboard.add(btns[0], btns[1])
    keyboard.add(btns[2], btns[3])
    return keyboard


def call_settings_keyboard(lang):
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btns = get_main_keyboard_btns(lang, settings=True)
    keyboard.add(btns[0], btns[1])
    keyboard.add(btns[2], btns[3])
    keyboard.add(btns[4], btns[5])
    keyboard.add(btns[6])
    return keyboard


# handle phenomenon inline keyboard
def gen_markup_phenomena(user_id, lang):
    markup = InlineKeyboardMarkup(row_width=2)

    for idx in range(0, len(phenomena_list) - 2, 2):
        temp_button_dict = {}
        for temp_btn in temp_buttons[:2]:
            phenomenon = phenomena_list[idx]
            idx += 1
            if Phenomenon.query.filter_by(user_id=user_id, phenomenon=phenomenon).first():
                tick = '✅ '
            else:
                tick = '✖'
            temp_button_dict[temp_btn] = InlineKeyboardButton(f"{tick}{inline_buttons[phenomenon][lang]}",
                                                              callback_data=f"phenomenon {phenomenon}")
        button_values = [v for k, v in temp_button_dict.items()]
        markup.add(button_values[0], button_values[1])

    if Phenomenon.query.filter_by(user_id=user_id, phenomenon=phenomena_list[-1]).first():
        tick = '✅ '
    else:
        tick = '✖'
    markup.add(
        InlineKeyboardButton(
            f"{tick}{inline_buttons[phenomena_list[-1]][lang]}", callback_data='phenomenon intense heat'),
        InlineKeyboardButton(f"{inline_buttons['manually'][lang]}", callback_data='phenomena manually'),
        InlineKeyboardButton(f"{inline_buttons['all phenomena'][lang]}", callback_data='all phenomena'),
        InlineKeyboardButton(f"{inline_buttons['set time'][lang]}", callback_data='set time phenomena')
    )
    return markup


ph_manually_list = ['positive temperature', 'negative temperature', 'wind speed', 'humidity']
additional_btns = ['remove all', 'back']


# handle phenomenon inline keyboard
def gen_markup_phenomena_manually(user_id, lang):
    markup = InlineKeyboardMarkup(row_width=1)
    for idx in range(0, len(ph_manually_list) - 1, 2):
        temp_button_dict = {}
        for temp_btn in temp_buttons[:2]:
            phenomenon = ph_manually_list[idx]
            idx += 1
            if PhenomenonManually.query.filter_by(user_id=user_id, phenomenon=phenomenon).first():
                tick = '✅ '
            else:
                tick = '✖'
            temp_button_dict[temp_btn] = InlineKeyboardButton(f"{tick}{inline_buttons[phenomenon][lang]}",
                                                              callback_data=f"manually {phenomenon}")
        button_values = [v for k, v in temp_button_dict.items()]
        markup.add(button_values[0], button_values[1])
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton(
            f"{inline_buttons[additional_btns[0]][lang]}", callback_data=f"manually {additional_btns[0]}"),
        InlineKeyboardButton(
            f"{inline_buttons[additional_btns[1]][lang]}", callback_data=f"manually {additional_btns[1]}")
    )
    return markup


def gen_markup_hours(user_id, model, lang, callback='', ):
    markup = InlineKeyboardMarkup(row_width=4)
    for hours in range(0, 24, 4):
        temp_button_dict = {}
        for temp_btn in temp_buttons:
            if model.query.filter_by(user_id=user_id, hours=hours).first():
                tick = '✅ '
            else:
                tick = '✖'
            temp_button_dict[temp_btn] = InlineKeyboardButton(f"{tick}{hours:0>2}:00",
                                                              callback_data=f"{hours:0>2}hr{callback}")
            hours += 1
        button_values = [v for k, v in temp_button_dict.items()]
        markup.add(button_values[0], button_values[1], button_values[2], button_values[3])
    if callback == '_ph':
        markup.add(InlineKeyboardButton(
            inline_buttons['back'][lang], callback_data=f"back_to{callback}"))
    else:
        markup.add(InlineKeyboardButton(
            f"{inline_buttons['remove all'][lang]}", callback_data="daily remove all"))
    return markup


def gen_markup_minutes(user_id, hours, model, lang, callback='', ):
    markup = InlineKeyboardMarkup(row_width=3)
    for mins in range(0, 60, 30):
        temp_button_dict = {}
        for temp_btn in temp_buttons[:3]:
            if model.query.filter_by(user_id=user_id, hours=hours, minutes=mins).first():
                tick = '✅ '
            else:
                tick = '✖'
            temp_button_dict[temp_btn] = InlineKeyboardButton(f"{tick}{hours}:{mins:0>2}",
                                                              callback_data=f"{hours}:{mins:0>2}min{callback}")
            mins += 10
        button_values = [v for k, v in temp_button_dict.items()]
        markup.add(button_values[0], button_values[1], button_values[2])
    markup.add(InlineKeyboardButton(inline_buttons['back'][lang], callback_data=f"back_to_hours{callback}"))
    return markup


# handle language inline keyboard
def gen_markup_language(user_id):
    markup = InlineKeyboardMarkup(row_width=2)
    btns_list = ['English', 'Русский']
    callback_list = ['english', 'russian']
    idx = 0
    temp_button_dict = {}
    for temp_btn in temp_buttons[:2]:
        if User.query.filter_by(id=user_id, language=callback_list[idx][:2].lower()).first():
            tick = '✅ '
        else:
            tick = '✖'
        temp_button_dict[temp_btn] = InlineKeyboardButton(f"{tick}{btns_list[idx]}",
                                                          callback_data=f"{callback_list[idx]}")
        idx += 1
    button_values = [v for k, v in temp_button_dict.items()]

    markup.add(button_values[0], button_values[1])
    return markup
