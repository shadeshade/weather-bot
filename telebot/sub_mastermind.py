import json
import os
import urllib.request

import requests
import transliterate
from bs4 import BeautifulSoup

CUR_PATH = os.path.realpath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(CUR_PATH))
DATA_DIR = os.path.join(BASE_DIR, 'data')


def get_cities_data():
    '''returns the CITIES_DB dictionary'''
    with open(os.path.join(DATA_DIR, 'cities_db.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def transliterate_name(city_to_translit):
    '''transliterates a city name for the get_response function in case the name is not in the cities_db'''
    if city_to_translit.title() in get_cities_data():
        return get_cities_data()[city_to_translit.title()]
    else:
        try:
            new_name = transliterate.translit(city_to_translit, reversed=True)
            if 'х' in city_to_translit.lower():
                new_name = new_name.lower().replace('h', 'kh')
        except:
            new_name = city_to_translit
        return new_name


def get_weather_info(city_name):
    '''returns the current weather info'''
    source = requests.get('https://yandex.ru/pogoda/' + city_name)
    soup = BeautifulSoup(source.content, 'html.parser')

    weather_soup = soup.find('div', attrs={'class': 'fact'})

    # with open('scrabed_file.html', 'w', encoding='utf-8') as f:
    #     f.write(soup.prettify())

    temperature = weather_soup.find('div', attrs={'class': 'fact__temp-wrap'})
    temperature = temperature.find(attrs={'class': 'temp__value'}).text

    image_src = weather_soup.find('div', attrs={'class': 'fact__temp-wrap'})
    image_src = image_src.find('img', attrs={'class': 'icon'})['src']  # appropriate weather image

    wind_speed = weather_soup.find('div', attrs={'class': 'fact__props'})
    wind_speed = wind_speed.find('div', attrs={'class': 'term__value'}).text  # wind speed and direction

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

    content = {
        'temperature': temperature,
        'image_src': image_src,
        'wind_speed': wind_speed,
        'humidity': humidity,
        'condition': condition,
        'feels_like': feels_like,
        'daylight_hours': daylight_hours,
        'sunrise': sunrise,
        'sunset': sunset,
    }
    return content

#
# def get_image(city_name):
#     '''returns the current weather image'''
#     source = requests.get('https://yandex.ru/pogoda/' + city_name)
#     soup = BeautifulSoup(source.content, 'html.parser')
#     image = soup.find('div', attrs={'class': 'fact__temp-wrap'})
#     image = image.find('img', attrs={'class': 'icon'})
#     image_src = image['src']
#     print(image_src)
#
#     file_name = DATA_DIR + '/' + city_name
#     urllib.request.urlretrieve('https:' + image_src, file_name)
#     return file_name


if __name__ == '__main__':
    (get_weather_info('Almaty'))
    # get_image('almaty')
    # get_cities_data()
