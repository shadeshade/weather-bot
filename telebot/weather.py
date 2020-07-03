# import transliterate
import json
from bs4 import BeautifulSoup
import requests
from telebot.mastermind import get_response


city = 'moscow'
source = requests.get('https://yandex.ru/pogoda/' + city)

# with open('cities_bd.json', 'r', encoding='utf-8') as f:
#     data1 = json.load(f)
#
# print(data1)

soup = BeautifulSoup(source.content, 'lxml')
temp = soup.find('div', class_='fact__temp-wrap')
temp = temp.find(class_='temp__value').text

print(temp)