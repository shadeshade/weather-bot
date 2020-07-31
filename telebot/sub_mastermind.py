import json
import os

import requests
import transliterate
from bs4 import BeautifulSoup


def get_temperature(city_name):
    '''returns the current temperature'''
    try:
        source = requests.get('https://yandex.ru/pogoda/' + city_name)
        soup = BeautifulSoup(source.content, 'lxml')
        temperature = soup.find('div', class_='fact__temp-wrap')
        temperature = temperature.find(class_='temp__value').text
    except:
        temperature = 'Try again'
    return temperature


def get_cities_data():
    '''returns the CITIES_DB dictionary'''
    CUR_PATH = os.path.realpath(__file__)
    BASE_DIR = os.path.dirname(os.path.dirname(CUR_PATH))
    DATA_DIR = os.path.join(BASE_DIR, 'data')

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


if __name__ == '__main__':
    pass
