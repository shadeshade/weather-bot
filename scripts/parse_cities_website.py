from bs4 import BeautifulSoup
import requests
import json

site1 = 'https://www.homeenglish.ru/Othercityworld.htm'
site2 = 'https://www.homeenglish.ru/Othercityrussia.htm'
source = requests.get(site2).content
soup = BeautifulSoup(source, 'lxml')

with open('cities_data3.json', 'w', encoding='utf-8') as f:
    cities_dict = {}

    city_names = soup.find(class_='wp-table')
    cities = city_names.find_all('tr')

    for city_name in cities:
        if len(city_name.text) > 4:

            ru_eng_names = []

            for item in city_name.find_all('td'):
                item = item.text.split(',')[0]
                ru_eng_names.append(item)

            cities_dict[ru_eng_names[0]] = ru_eng_names[1]
    json.dump(cities_dict, f, ensure_ascii=False, indent=4)
