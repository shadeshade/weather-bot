import os

import transliterate
import json
from bs4 import BeautifulSoup
import requests

CUR_PATH = os.path.realpath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(CUR_PATH))
DATA_DIR = os.path.join(BASE_DIR, 'data')

with open(os.path.join(DATA_DIR, 'cities_bd.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)


def translit_name(name):
    if name.title() in data:
        return data[name.title()]
    else:
        try:
            new_name = transliterate.translit(name, reversed=True)
            if 'х' in name.lower():
                new_name = new_name.lower().replace('h', 'kh')
        except:
            new_name = name
        return new_name


def get_response(city_name):
    city = translit_name(city_name)
    try:
        source = requests.get('https://yandex.ru/pogoda/' + city)
        soup = BeautifulSoup(source.content, 'lxml')
        temp = soup.find('div', class_='fact__temp-wrap')
        temp = temp.find(class_='temp__value').text
    except:
        temp = 'Try again'
    return temp


if __name__ == '__main__':
    print(get_response('ТэджоН'))
