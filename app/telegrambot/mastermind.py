import json
import os

import requests
import transliterate
from bs4 import BeautifulSoup

CUR_PATH = os.path.realpath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(CUR_PATH))
DATA_DIR = os.path.join(BASE_DIR, 'data')
STATIC_DIR = os.path.join(BASE_DIR, 'static')


def get_response(city_name):
    """basic function"""
    transliterated_city = transliterate_name(city_name)

    try:
        weather_info = get_weather_info(transliterated_city)
    except:
        return 'Try again'

    response_message = f'{weather_info["temperature"]}°C,\n' \
                       f'{weather_info["wind_speed"]}\n' \
                       f'{weather_info["condition"]}  ⛅\n' \
                       f'Ощущается Как: {weather_info["feels_like"]}\n' \
                       f'Световой День: {weather_info["daylight_hours"]}\n' \
                       f'Восход - Закат: {weather_info["sunrise"]} - {weather_info["sunset"]}'

    return response_message


def get_weather_info(city_name):
    """return the current weather info"""
    source = requests.get('https://yandex.ru/pogoda/' + city_name)
    soup = BeautifulSoup(source.content, 'html.parser')

    weather_soup = soup.find('div', attrs={'class': 'fact'})

    # with open('scrabed_file.html', 'w', encoding='utf-8') as f:
    #     f.write(soup.prettify())

    temperature = weather_soup.find('div', attrs={'class': 'fact__temp-wrap'})
    temperature = temperature.find(attrs={'class': 'temp__value'}).text

    image_src = weather_soup.find('div', attrs={'class': 'fact__temp-wrap'})
    image_src = image_src.find('img', attrs={'class': 'icon'})['src']  # appropriate weather image

    wind_speed_and_direction = weather_soup.find('div', attrs={'class': 'fact__props'})
    try:
        wind_speed = wind_speed_and_direction.find('span', attrs={'class': 'wind-speed'}).text  # wind speed
        wind_direction = wind_speed_and_direction.find('abbr')['title']  # wind direction
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

    # extended_weather_soup = soup.find('ul', attrs={'class': 'swiper-wrapper'})
    # weather_time = extended_weather_soup.find('div', attrs={'class': 'fact__hour-label'}).text
    # weather_temperature = extended_weather_soup.find('div', attrs={'class': 'fact__hour-temp'}).text

    response_message = {
        'temperature': temperature,
        'image_src': image_src,
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


# temp
def get_scrap():
    source = requests.get('https://yandex.ru/pogoda/makhachkala/details')
    soup = BeautifulSoup(source.content, 'html.parser')
    weather_table = soup.find('table', attrs={'class': 'weather-table'})

    with open(os.path.join(DATA_DIR, 'scraped.html'), 'w', encoding='utf-8') as f:
        f.write(soup.prettify())

    pass


def get_next_day(city_name):
    """get tomorrow's weather info"""
    transliterated_city = transliterate_name(city_name)
    extended_info = get_extended_info(transliterated_city, 'tomorrow')

    response_message = f'{extended_info["part1"]["weather_daypart"]},\n' \
                       f'{extended_info["part1"]["weather_daypart_temp"]},\n' \
                       f'{extended_info["part1"]["weather_daypart_condition"]},\n' \
                       f'{extended_info["part1"]["weather_daypart_wind"]},\n' \
                       f'{extended_info["part1"]["weather_daypart_direction"]},\n'

    return response_message


def get_next_week(city_name):
    """get next 7 day's weather info"""
    transliterated_city = transliterate_name(city_name)
    extended_info = get_extended_info(transliterated_city, 'week')

    response_message = f'{extended_info["part1"]["weather_daypart"]},\n' \
                       f'{extended_info["part1"]["weather_daypart_temp"]},\n' \
                       f'{extended_info["part1"]["weather_daypart_condition"]},\n' \
                       f'{extended_info["part1"]["weather_daypart_wind"]},\n' \
                       f'{extended_info["part1"]["weather_daypart_direction"]},\n'

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


def get_extended_info(city_name, command):
    """return the extended weather info of the current day for daily cast"""
    source = requests.get('https://yandex.ru/pogoda/' + city_name + '/details')
    soup = BeautifulSoup(source.content, 'html.parser')

    if command == 'daily':
        weather_table = soup.find('table', attrs={'class': 'weather-table'})
    elif command == 'tomorrow':
        weather_table = soup.find_all('table', attrs={'class': 'weather-table'})[1]
    else:
        # command == 'week'
        days_dict = dict()
        day_count = 0
        weather_tables = soup.find_all('table', attrs={'class': 'weather-table'})
        for table in weather_tables:
            weather_rows = table.find_all('tr', attrs={'class': 'weather-table__row'})
            daypart_dict = dict()
            day_count += 1
            row_count = 0
            for row in weather_rows:
                weather_daypart = row.find('div', attrs={'class': 'weather-table__daypart'}).text
                weather_daypart_temp = row.find('div', attrs={'class': 'weather-table__temp'}).text
                weather_daypart_condition = row.find('td',
                                                     attrs={'class': 'weather-table__body-cell_type_condition'}).text
                temp_daypart_dict = {
                    'weather_daypart': weather_daypart,
                    'weather_daypart_temp': weather_daypart_temp,
                    'weather_daypart_condition': weather_daypart_condition,
                }
                row_count += 1
                part_num = str(row_count)
                daypart_dict['part' + part_num] = temp_daypart_dict
            days_dict['day' + str(day_count)] = daypart_dict

        return days_dict

    weather_rows = weather_table.find_all('tr', attrs={'class': 'weather-table__row'})

    daypart_dict = dict()
    count = 0
    for row in weather_rows:
        weather_daypart = row.find('div', attrs={'class': 'weather-table__daypart'}).text
        weather_daypart_temp = row.find('div', attrs={'class': 'weather-table__temp'}).text
        weather_daypart_condition = row.find('td', attrs={'class': 'weather-table__body-cell_type_condition'}).text
        try:
            weather_daypart_wind = row.find('span', attrs={'class': 'weather-table__wind'}).text
            weather_daypart_direction = row.find('abbr')['title']
        except:
            weather_daypart_wind = 'Штиль'
            weather_daypart_direction = ''

        temp_daypart_dict = {
            'weather_daypart': weather_daypart,
            'weather_daypart_temp': weather_daypart_temp,
            'weather_daypart_condition': weather_daypart_condition,
            'weather_daypart_wind': weather_daypart_wind,
            'weather_daypart_direction': weather_daypart_direction
        }
        count += 1
        part_num = str(count)
        daypart_dict['part' + part_num] = temp_daypart_dict

    return daypart_dict


def get_start(first_name):
    """returns greeting and a short navigate information"""
    text = f'<b>Hello, {first_name} !\nPlease, type your location</b> 🌏 \n\nFor more options use /help'
    return text


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


def get_cities_data():
    """return the cities_db dictionary"""
    with open(os.path.join(DATA_DIR, 'cities_db.json'), 'r', encoding='utf-8') as f:
        cities_data = json.load(f)
    content = {'cities_data': cities_data}
    return content


def transliterate_name(city_to_translit):
    """transliterate a city name for the get_response function in case the name is not in the cities_db"""
    if city_to_translit.title() in get_cities_data()['cities_data']:
        return get_cities_data()['cities_data'][city_to_translit.title()]
    else:
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
    get_next_day('moscow')
