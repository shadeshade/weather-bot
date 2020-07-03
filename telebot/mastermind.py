import transliterate
import json
from bs4 import BeautifulSoup
import requests

with open('cities_bd.json', 'r', encoding='utf-8') as f:
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


def get_response(city):
    city = translit_name(city)
    source = requests.get('https://yandex.ru/pogoda/' + city)
    soup = BeautifulSoup(source.content, 'lxml')
    temp = soup.find('div', class_='fact__temp-wrap')
    temp = temp.find(class_='temp__value').text
    return temp