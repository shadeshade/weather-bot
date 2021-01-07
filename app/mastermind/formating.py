from datetime import datetime
from typing import Dict

import transliterate
from transliterate.exceptions import LanguageDetectionError

from app import logger
from app.data import emoji_conditions
from app.data.localization import hints, info, phenomenon_button_names, phenomenon_aliases
from app.data.utils import get_city_data
from app.mastermind.parsing import get_weather_info, get_extended_info, get_extended_info_for_week
from app.models import Phenomenon


def get_start(first_name, lang):
    """returns greeting and a short navigate information"""
    text = hints['start msg1'][lang] + first_name + hints['start msg2'][lang]
    return text


def transliterate_name(city_to_translit):
    """transliterate a city name in case the name is not in the cities_db"""
    try:
        city = get_city_data(city_to_translit.title())
    except KeyError as e:
        logger.warning(f'There is no such a city in the db {repr(e)}')
    else:
        return city

    try:
        new_name = transliterate.translit(city_to_translit, reversed=True)  # ru -> en
        if 'х' in city_to_translit.lower():  # 'х'(rus) -> 'kh'
            new_name = new_name.lower().replace('h', 'kh')
    except LanguageDetectionError as e:
        logger.warning(f'The name of the city is not in Russian. ({e})')
        new_name = city_to_translit
    return new_name


def get_day_part(ts, sunrise, sunset):  # timestamp in Unix time
    if isinstance(ts, int):
        msg_time = datetime.fromtimestamp(ts).strftime('%H:%M').replace(':', '.')
    else:
        msg_time = ts
    sunrise = sunrise.replace(':', '.')
    sunset = sunset.replace(':', '.')
    if float(msg_time) > float(sunset) or float(msg_time) < float(sunrise):
        return 'night'
    else:
        return 'day'


def get_condition(cond, day_part):
    """"return emoji from the dictionary"""
    daylight_time = ['morning', 'day', 'утром', 'днём']

    if day_part.lower() not in daylight_time:
        try:
            condition = emoji_conditions.cond_emoji_night[cond.lower()]
            return condition.title()
        except KeyError as e:
            logger.warning(f'Condition has not been found\n{e}')
            try:
                translated = emoji_conditions.cond_trans_reversed[cond.lower()]
                condition = emoji_conditions.cond_emoji_night[translated.lower()]
                return condition.title()
            except KeyError as e:
                logger.warning(f'Condition has not been found\n{e}')

    try:
        condition = emoji_conditions.cond_emoji[cond.lower()]
    except KeyError as e:
        logger.warning(f'Condition has not been found\n{e}')
        try:
            translated = emoji_conditions.cond_trans_reversed[cond.lower()]
            condition = emoji_conditions.cond_emoji[translated.lower()]
        except KeyError as e:
            logger.warning(f'Condition has not been found\n{e}')
            return ''
    return condition.title()


def get_today_weather_info(city_name, lang, cur_timestamp):
    """basic function to get weather info for today"""

    transliterated_city = transliterate_name(city_name)

    try:
        weather_info = get_weather_info(transliterated_city, lang)
    except AttributeError as e:
        logger.error(f'Wrong city name\n{e}')
        return info[lang][0]
    else:
        weather_rest_info = get_extended_info(transliterated_city, 'today', lang)  # type: Dict

    daypart_message = ''
    for i in range(1, 5):
        daypart_info = weather_rest_info["part" + str(i)]  # type: Dict[str, str]
        daypart = daypart_info["weather_daypart"]
        daypart_temp = daypart_info["weather_daypart_temp"]
        daypart_cond = daypart_info["weather_daypart_condition"]
        daypart_cond_emoji = get_condition(daypart_cond, daypart)

        wind_speed_and_direction = daypart_info["wind_speed_and_direction"]
        if wind_speed_and_direction != info[lang][7]:
            wind_speed_and_direction = wind_speed_and_direction.split(', ')[0]

        daypart_message += f'{daypart.title()}: {daypart_temp}; {info[lang][2]}: {wind_speed_and_direction} ' \
                           f'{daypart_cond_emoji}\n\n'

    header = weather_info["header"]
    temp = weather_info["temperature"]
    wind_speed_and_direction = weather_info["wind_speed_and_direction"]
    humidity = weather_info["humidity"]
    cond = weather_info["condition"]
    feels_like = weather_info["feels_like"]
    daylight_hours = weather_info["daylight_hours"]
    sunrise = weather_info["sunrise"]
    sunset = weather_info["sunset"]

    day_time = get_day_part(cur_timestamp, sunrise, sunset)
    weather_cond = get_condition(cond, day_time)

    message_part1 = f'<i>{header}</i>\n\n' \
                    f'<b>{info[lang][1]}: {temp}°; {info[lang][3]}: {feels_like}\n' \
                    f'{info[lang][2]}: {wind_speed_and_direction}; {phenomenon_button_names["humidity"][lang]}:' \
                    f' {humidity}\n' \
                    f'{cond} {weather_cond}</b> \n\n'

    message_part2 = f'{info[lang][4]}: {daylight_hours}\n' \
                    f'{info[lang][5]}: {sunrise} - {sunset}\n'

    response_message = message_part1 + daypart_message + message_part2

    return response_message


def get_next_day(city_name, lang, phenomenon_info=False):
    """get tomorrow's weather info"""
    transliterated_city = transliterate_name(city_name)
    extended_info = get_extended_info(transliterated_city, 'tomorrow', lang)  # type: Dict
    if phenomenon_info:
        response_dict = {}
        daypart = 1
        for weather_val in extended_info.values():
            daypart_temp = weather_val["weather_daypart_temp"]
            daypart_condition = weather_val["weather_daypart_condition"]
            daypart_wind = weather_val["wind_speed_and_direction"].split(info[lang][10])[0].strip()
            daypart_humidity = weather_val["weather_daypart_humidity"]

            temp_daypart_dict = {
                'daypart_temp': daypart_temp,
                'daypart_condition': daypart_condition,
                'daypart_wind': daypart_wind,
                'daypart_humidity': daypart_humidity,
            }
            response_dict['part' + str(daypart)] = temp_daypart_dict
            daypart += 1
            if daypart > 4:
                break
        return response_dict

    response_message = f'<i>{extended_info["weather_city"]} {info[lang][6]} {extended_info["weather_date"]}</i>\n\n'
    for num in range(1, 5):
        daypart_info = extended_info["part" + str(num)]  # type: Dict[str, str]
        cond = daypart_info["weather_daypart_condition"]
        weather_daypart = daypart_info["weather_daypart"]
        daypart_temp = daypart_info["weather_daypart_temp"]
        wind_speed_and_direction = daypart_info["wind_speed_and_direction"]
        response_message += f'<b>{weather_daypart.title()}</b>, {daypart_temp} ' \
                            f'{info[lang][2]}: {wind_speed_and_direction}' \
                            f'\n{cond} {get_condition(cond, weather_daypart)}\n\n'

    daylight_hours = f'{info[lang][4]}: {extended_info["daylight_hours"]}\n' \
                     f'{info[lang][5]}: {extended_info["sunrise"]} - {extended_info["sunset"]}\n'
    response_message += daylight_hours

    return response_message


def get_next_week(city, lang):
    """get next 7 day's weather info"""
    transliterated_city = transliterate_name(city)
    extended_info = get_extended_info_for_week(transliterated_city, lang)
    response_message = ''
    weather_city = extended_info.pop('weather_city')
    for day in extended_info.values():
        day_info_message = ''
        for day_part_key, day_part_value in day.items():
            if 'part' not in day_part_key:
                continue

            weather_daypart = day_part_value['weather_daypart'].title()
            weather_daypart_temp = day_part_value['weather_daypart_temp']
            weather_daypart_condition = day_part_value['weather_daypart_condition']
            wind_speed_and_direction = day_part_value['wind_speed_and_direction']
            weather_cond = get_condition(weather_daypart_condition, weather_daypart)
            day_info_message += f'{weather_daypart}: {weather_daypart_temp}; ' \
                                f' {wind_speed_and_direction} {weather_cond}\n'

        weather_date = day['weather_date']
        day_info_message = f'\n<i><b>{weather_date}</b></i>\n{day_info_message}'  # date + weather info
        response_message += day_info_message

    response_message = f'<i>{weather_city}. {info[lang][8]}</i>\n{response_message}'

    return response_message


def get_daily(city_name, lang):
    """daily info"""
    transliterated_city = transliterate_name(city_name)
    extended_info = get_extended_info(transliterated_city, 'daily', lang)
    response_message = f'{extended_info["part1"]["weather_daypart"]},\n' \
                       f'{extended_info["part1"]["weather_daypart_temp"]},\n' \
                       f'{extended_info["part1"]["weather_daypart_condition"]},\n' \
                       f'{extended_info["part1"]["weather_daypart_wind"]},\n' \
                       f'{extended_info["part1"]["weather_daypart_direction"]},\n'
    return response_message


def get_phenomenon_info(user):
    """Handle phenomenon reminder (sending a reminder)"""
    next_day_max_val = {'temp_min': None, 'temp_max': None, 'condition': [], 'wind': 0, 'humidity': 0}
    user_id = user.id
    lang = user.language
    all_phenomena = Phenomenon.query.filter_by(user_id=user_id).all()
    next_day_info = get_next_day(user.city_name, lang, phenomenon_info=True)

    for day_part_info in next_day_info.values():
        temp = day_part_info['daypart_temp'].split('…')
        temp_min = temp[0].replace('°', '')
        try:
            temp_max = temp[1].replace('°', '')
        except IndexError as e:
            logger.warning(f'Only one value\n{repr(e)}')
            temp_max = temp_min

        if next_day_max_val['temp_min'] is None:
            next_day_max_val['temp_min'] = temp_min
            next_day_max_val['temp_max'] = temp_max
        else:
            if temp_min < next_day_max_val['temp_min']:
                next_day_max_val['temp_min'] = temp_min
            elif temp_max > next_day_max_val['temp_max']:
                next_day_max_val['temp_max'] = temp_max

        condition = day_part_info['daypart_condition']  # condition
        next_day_max_val['condition'] += [condition.lower()]

        wind = float(day_part_info['daypart_wind'].replace(',', '.'))  # wind
        if wind > next_day_max_val['wind']:
            next_day_max_val['wind'] = wind

        humidity = int(day_part_info['daypart_humidity'].replace('%', ''))  # humidity
        if humidity > next_day_max_val['humidity']:
            next_day_max_val['humidity'] = humidity

    temp_min = next_day_max_val['temp_min']
    temp_max = next_day_max_val['temp_max']
    condition = next_day_max_val['condition']
    wind = next_day_max_val['wind']
    humidity = next_day_max_val['humidity']

    text = ''
    # checking if phenomena expected tomorrow
    phenomena_list = [ph for ph in all_phenomena if ph.is_manually is False]
    for phenomenon in phenomena_list:
        existing_ph = phenomenon_button_names[phenomenon.phenomenon][lang].lower()
        if existing_ph not in text and phenomenon.phenomenon in phenomenon_aliases.keys():
            for cond in condition:
                if cond in phenomenon_aliases[phenomenon.phenomenon][lang]:
                    text += f'\n{cond.capitalize()}'
                    break
            continue
        elif existing_ph == phenomenon_button_names["strong wind"][lang].lower():
            if 29 >= wind >= 12:
                val_and_unit = f'{wind} {info[lang][10]}'
                pass
            else:
                continue
        elif existing_ph == phenomenon_button_names["hurricane"][lang].lower():
            if wind >= 30:
                val_and_unit = f'{wind} {info[lang][10]}'
                pass
            else:
                continue
        elif existing_ph == phenomenon_button_names["intense heat"][lang].lower():
            if int(temp_max) >= 30:
                val_and_unit = f'+{temp_max}°C'
                pass
            else:
                continue
        else:
            continue
        text += f'\n{existing_ph.capitalize()} {val_and_unit}'

    # checking if manual phenomena expected tomorrow
    man_phenomena_list = [ph for ph in all_phenomena if ph.is_manually is True]
    for man_ph in man_phenomena_list:
        ph = phenomenon_button_names[man_ph.phenomenon][lang].lower()
        val = int(man_ph.value)
        if ph == phenomenon_button_names['temperature more'][lang].lower() \
                or ph == phenomenon_button_names['temperature less'][lang].lower():
            if ph == phenomenon_button_names['temperature more'][lang].lower():
                if val <= int(temp_max):
                    pass
                else:
                    continue
            elif ph == phenomenon_button_names['temperature less'][lang].lower():
                if val >= int(temp_min):
                    pass
                else:
                    continue
            if '°C' not in text:
                if temp_min != temp_max:
                    val_and_unit = f'{temp_min}°C...{temp_max}°C'
                else:
                    val_and_unit = f'{temp_min}°C'
            else:
                continue
            ph = info[lang][11]
        elif ph == phenomenon_button_names['wind speed'][lang].lower():
            if val <= wind:
                val_and_unit = f'{wind} {info[lang][10]}'
                pass
            else:
                continue
        elif ph == phenomenon_button_names['humidity'][lang].lower():
            if val <= humidity:
                val_and_unit = f'{humidity}%'
                pass
            else:
                continue
        else:
            continue

        text += f'\n{ph.capitalize()}: {val_and_unit}'

    if text:
        response_msg = f'<b>{hints["phenomenon tomorrow"][lang]}</b>'
        response_msg += text
        return response_msg
    else:
        return None
