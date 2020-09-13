import json
import os
from typing import Dict

import requests
import transliterate
from bs4 import BeautifulSoup

from app.data import emoji_condition_db

CUR_PATH = os.path.realpath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(CUR_PATH))
DATA_DIR = os.path.join(BASE_DIR, 'data')
STATIC_DIR = os.path.join(BASE_DIR, 'static')


def get_condition(cond):
    """"return emoji from the dictionary"""
    try:
        condition = emoji_condition_db.cond_emoji[cond.lower()]
    except:
        translated = emoji_condition_db.cond_trans_reversed[cond.lower()]
        condition = emoji_condition_db.cond_emoji[translated.lower()]
    return condition.title()


def get_start(first_name):
    """returns greeting and a short navigate information"""
    text = f'<b>Hello, {first_name} !\nPlease, type your location</b> 🌏 \n\nFor more options use /help'
    return text


def get_response(city_name, lang):
    """basic function"""
    transliterated_city = transliterate_name(city_name)

    try:
        weather_info = get_weather_info(transliterated_city, lang)
        weather_rest_info = get_extended_info(transliterated_city, 'today', lang)  # type: Dict
    except:
        return 'Try again'

    daypart_message = ''
    for i in range(1, 5):
        daypart_info = weather_rest_info["part" + str(i)]  # type: Dict[str, str]
        daypart = daypart_info["weather_daypart"]
        daypart_temp = daypart_info["weather_daypart_temp"]
        daypart_cond = daypart_info["weather_daypart_condition"]
        daypart_cond_emoji = get_condition(daypart_cond)
        daypart_wind = daypart_info["weather_daypart_wind"]
        daypart_wind_unit = daypart_info["weather_unit"]
        daypart_wind_direct = daypart_info["weather_daypart_direction"]

        daypart_message += f'{daypart.title()}: {daypart_temp}; {daypart_wind_direct} {daypart_wind}' \
                           f' {daypart_wind_unit} {daypart_cond_emoji}\n\n'

    header = weather_info["header"]
    temp = weather_info["temperature"]
    wind_speed = weather_info["wind_speed"]
    wind_direct = weather_info["wind_direction"]
    cond = weather_info["condition"]
    cond_emoji = get_condition(cond)
    feels_like = weather_info["feels_like"]
    daylight_hours = weather_info["daylight_hours"]
    sunrise = weather_info["sunrise"]
    sunset = weather_info["sunset"]

    message_part1 = f'<i>{header}</i>\n\n' \
                    f'<b>Сейчас: {temp}°C, {cond}  {cond_emoji}\n' \
                    f'ветер: {wind_speed} {wind_direct}, ' \
                    f'ощущается как: {feels_like}</b> \n\n\n'

    message_part2 = f'\nСветовой день: {daylight_hours}\n' \
                    f'Восход - Закат: {sunrise} - {sunset}\n'

    response_message = message_part1 + daypart_message + message_part2

    return response_message


def get_weather_info(city_name, lang):
    """return the current weather info"""
    if lang == 'ru':
        source = requests.get('https://yandex.ru/pogoda/' + city_name)

    else:
        source = requests.get('https://yandex.com/pogoda/' + city_name)

    soup = BeautifulSoup(source.content, 'html.parser')
    weather_soup = soup.find('div', attrs={'class': 'fact'})

    header = weather_soup.find('div', attrs={'class': 'header-title'})
    header = header.find('h1', attrs={'class': 'title'}).text

    temperature = weather_soup.find('div', attrs={'class': 'fact__temp-wrap'})
    temperature = temperature.find(attrs={'class': 'temp__value'}).text

    wind_speed_and_direction = weather_soup.find('div', attrs={'class': 'fact__props'})
    try:
        wind_speed = wind_speed_and_direction.find('span', attrs={'class': 'wind-speed'}).text  # wind speed
        wind_direction = wind_speed_and_direction.find('span', attrs={'class': 'fact__unit'}).text  # wind unit, direct
        # wind_direction = wind_speed_and_direction.find('abbr')['title']  # wind direction

    except:
        wind_speed = 'Штиль'
        wind_direction = ''

    humidity = weather_soup.find('div', attrs={'class': 'fact__humidity'})
    humidity = humidity.find('div', attrs={'class': 'term__value'}).text  # humidity percentage

    condition = weather_soup.find('div', attrs={
        'class': 'link__condition'}).text  # condition comment (clear, windy etc.)

    feels_like = weather_soup.find('div', attrs={'class': 'term__value'})
    feels_like = feels_like.find('div', attrs={'class': 'temp'}).text  # feels like temperature

    daylight_soup = soup.find('div', attrs={'class': 'sun-card__info'})
    daylight_hours = daylight_soup.find('div', attrs={
        'class': 'sun-card__day-duration-value'}).text  # daylight duration
    sunrise = daylight_soup.find('div', attrs={'class': 'sun-card__sunrise-sunset-info_value_rise-time'}).text[-5:]
    sunset = daylight_soup.find('div', attrs={'class': 'sun-card__sunrise-sunset-info_value_set-time'}).text[-5:]

    response_message = {
        'header': header,
        'temperature': temperature,
        'wind_speed': wind_speed,
        'wind_direction': wind_direction,
        'humidity': humidity,
        'condition': condition,
        'feels_like': feels_like,
        'daylight_hours': daylight_hours,
        'sunrise': sunrise,
        'sunset': sunset,
    }
    return response_message


def get_next_day(city_name, lang, cond_needed=False):
    """get tomorrow's weather info"""
    transliterated_city = transliterate_name(city_name)
    extended_info = get_extended_info(transliterated_city, 'tomorrow', lang)  # type: Dict
    if cond_needed:
        response_dict = {}
        daypart = 1
        for v in extended_info.values():
            try:
                cond = v["weather_daypart_condition"]
            except:
                break
            response_dict['part'+str(daypart)] = cond
            daypart += 1
        return response_dict

    response_message = f'<i>{extended_info["weather_city"]} на {extended_info["weather_date"]}</i>\n\n'
    for i in range(1, 5):
        daypart_info = extended_info["part" + str(i)]  # type: Dict[str, str]
        cond = daypart_info["weather_daypart_condition"]

        response_message += f'<b>{daypart_info["weather_daypart"].title()}</b>,' \
                            f' {daypart_info["weather_daypart_temp"]}\n' \
                            f'ветер: {daypart_info["weather_daypart_wind"]} {daypart_info["weather_unit"]}' \
                            f' {daypart_info["weather_daypart_direction"]}; {cond} {get_condition(cond)}\n\n'

    return response_message


def get_next_week(city_name, lang):
    """get next 7 day's weather info"""
    transliterated_city = transliterate_name(city_name)
    extended_info = get_extended_info(transliterated_city, 'week', lang)
    response_message = ''
    weather_city = extended_info['weather_city']
    try:
        for day in extended_info.values():
            day_info_message = ''
            for day_part in day.values():
                try:
                    weather_daypart = day_part['weather_daypart'].title()
                    weather_daypart_temp = day_part['weather_daypart_temp']
                    weather_daypart_condition = day_part['weather_daypart_condition']
                    weather_daypart_wind = day_part['weather_daypart_wind']
                    weather_daypart_direction = day_part['weather_daypart_direction']
                    weather_unit = day_part['weather_unit']
                    weather_cond = get_condition(weather_daypart_condition)
                    day_info_message += f'{weather_daypart}: {weather_daypart_temp}; {weather_daypart_direction}' \
                                        f' {weather_daypart_wind} {weather_unit} {weather_cond}\n'
                except:
                    day_info_message = f'\n<i><b>{day_part}</b></i>\n{day_info_message}'  # date + weather info
            response_message += day_info_message
    except:
        pass
    response_message = f'<i>{weather_city}. Погода на 7 дней</i>\n{response_message}'

    return response_message


# daily info
def get_daily(city_name, ):
    transliterated_city = transliterate_name(city_name)
    extended_info = get_extended_info(transliterated_city, 'daily')
    # part_nums = [1,2,3,4]
    # printing_message = ''
    # for num in part_nums:
    response_message = f'{extended_info["part1"]["weather_daypart"]},\n' \
                       f'{extended_info["part1"]["weather_daypart_temp"]},\n' \
                       f'{extended_info["part1"]["weather_daypart_condition"]},\n' \
                       f'{extended_info["part1"]["weather_daypart_wind"]},\n' \
                       f'{extended_info["part1"]["weather_daypart_direction"]},\n'
    # printing_message += response_message
    return response_message


# handle get_extended_info func
def get_day_info(weather_rows, weather_unit):
    daypart_dict = dict()
    row_count = 0
    for row in weather_rows:
        weather_daypart = row.find('div', attrs={'class': 'weather-table__daypart'}).text
        weather_daypart_temp = row.find('div', attrs={'class': 'weather-table__temp'}).text
        weather_daypart_condition = row.find('td', attrs={'class': 'weather-table__body-cell_type_condition'}).text
        try:
            weather_daypart_wind = row.find('span', attrs={'class': 'weather-table__wind'}).text
            weather_daypart_direction = row.find('abbr', attrs={'class': 'icon-abbr'}).text
        except:
            weather_daypart_wind = 'Штиль'
            weather_daypart_direction = ''

        temp_daypart_dict = {
            'weather_daypart': weather_daypart,
            'weather_daypart_temp': weather_daypart_temp,
            'weather_daypart_condition': weather_daypart_condition,
            'weather_daypart_wind': weather_daypart_wind,
            'weather_daypart_direction': weather_daypart_direction,
            'weather_unit': weather_unit,
        }
        row_count += 1
        daypart_dict['part' + str(row_count)] = temp_daypart_dict
    return daypart_dict


# handle 'daily', 'tomorrow', 'today', 'for a week' buttons
def get_extended_info(city_name, command, lang):
    """return the extended weather info of the current day for daily cast"""
    if lang == 'ru':
        source = requests.get('https://yandex.ru/pogoda/' + city_name + '/details')
        weather_unit = 'м/с'
    else:
        source = requests.get('https://yandex.com/pogoda/' + city_name + '/details')
        weather_unit = 'm/s'

    soup = BeautifulSoup(source.content, 'html.parser')

    if command == 'daily':  # button daily
        weather_table = soup.find('div', attrs={'class': 'card'})
    elif command == 'tomorrow':  # button tomorrow
        weather_table = soup.find_all('div', attrs={'class': 'card'})[2]
    elif command == 'today':
        weather_table = soup.find_all('div', attrs={'class': 'card'})[0]
    else:  # button for a week
        days_dict = dict()
        day_count = 0

        weather_city = soup.find('h1', attrs={'class': 'title title_level_1 header-title__title'}).text
        weather_city = weather_city.split()[-1]

        weather_tables = soup.find_all('div', attrs={'class': 'card'})[2:]
        for day in weather_tables:
            if day_count > 7:
                break
            weather_day = day.find('strong', attrs={'class': 'forecast-details__day-number'}).text
            weather_month = day.find('span', attrs={'class': 'forecast-details__day-month'}).text
            weather_date = f'{weather_day} {weather_month}'
            weather_rows = day.find_all('tr', attrs={'class': 'weather-table__row'})
            day_count += 1

            daypart_dict = get_day_info(weather_rows, weather_unit)
            daypart_dict['weather_date'] = weather_date
            days_dict['day' + str(day_count)] = daypart_dict

        days_dict['weather_city'] = weather_city
        return days_dict

    weather_city = soup.find('h1', attrs={'class': 'title title_level_1 header-title__title'}).text
    weather_city = weather_city.split()[-1]
    weather_day = weather_table.find('strong', attrs={'class': 'forecast-details__day-number'}).text
    weather_month = weather_table.find('span', attrs={'class': 'forecast-details__day-month'}).text
    weather_date = f'{weather_day} {weather_month}'
    weather_rows = weather_table.find_all('tr', attrs={'class': 'weather-table__row'})

    daypart_dict = get_day_info(weather_rows, weather_unit)
    daypart_dict['weather_city'] = weather_city
    daypart_dict['weather_date'] = weather_date

    return daypart_dict


def get_help():
    """returns commands list"""
    text = '/start:\nStart bot interaction.\n\n' \
           '/daily:\nSet daily time you want to receive weather information. More than one city addition is ' \
           'available\n\n' \
           '/remove_daily:\nChoose the city to remove from your daily info.\n\n' \
           '/reminder:\nSet reminder about the incoming event you want. E.g. receive a message that rain' \
           ' is expected in two days\n\n' \
           '/remove_reminder:\nChoose the reminder name to remove from your reminder list.'
    return text


def get_cities_data(city):
    """return the cities_db dictionary"""
    with open(os.path.join(DATA_DIR, 'cities_db.json'), 'r', encoding='utf-8') as f:
        cities_data = json.load(f)
    content = cities_data[city]
    return content


def transliterate_name(city_to_translit):
    """transliterate a city name for the get_response function in case the name is not in the cities_db"""
    try:
        city = get_cities_data(city_to_translit.title())
        return city
    except:
        pass

    try:
        new_name = transliterate.translit(city_to_translit, reversed=True)
        if 'х' in city_to_translit.lower():
            new_name = new_name.lower().replace('h', 'kh')
    except:
        new_name = city_to_translit
    return new_name


if __name__ == '__main__':
    # print(get_daily('маха'))
    # print(get_response('Питер'))
    # get_scrap()
    # get_next_day('moscow')
    get_condition('snow')
