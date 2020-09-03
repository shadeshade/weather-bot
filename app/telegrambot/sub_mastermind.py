# import json
# import os
# import requests
# import transliterate
# from bs4 import BeautifulSoup
#
# CUR_PATH = os.path.realpath(__file__)
# BASE_DIR = os.path.dirname(os.path.dirname(CUR_PATH))
# DATA_DIR = os.path.join(BASE_DIR, 'data')
# STATIC_DIR = os.path.join(BASE_DIR, 'static')
#
#
# def get_cities_data():
#     """return the cities_db dictionary"""
#     with open(os.path.join(DATA_DIR, 'cities_db.json'), 'r', encoding='utf-8') as f:
#         cities_data = json.load(f)
#     content = {'cities_data': cities_data}
#     return content
#
#
# def transliterate_name(city_to_translit):
#     """transliterate a city name for the get_response function in case the name is not in the cities_db"""
#     if city_to_translit.title() in get_cities_data()['cities_data']:
#         return get_cities_data()['cities_data'][city_to_translit.title()]
#     else:
#         try:
#             new_name = transliterate.translit(city_to_translit, reversed=True)
#             if 'х' in city_to_translit.lower():
#                 new_name = new_name.lower().replace('h', 'kh')
#         except:
#             new_name = city_to_translit
#         return new_name
#
#
# def get_weather_info(city_name):
#     """return the current weather info"""
#     source = requests.get('https://yandex.ru/pogoda/' + city_name)
#     soup = BeautifulSoup(source.content, 'html.parser')
#
#     weather_soup = soup.find('div', attrs={'class': 'fact'})
#
#     # with open('scrabed_file.html', 'w', encoding='utf-8') as f:
#     #     f.write(soup.prettify())
#
#     temperature = weather_soup.find('div', attrs={'class': 'fact__temp-wrap'})
#     temperature = temperature.find(attrs={'class': 'temp__value'}).text
#
#     image_src = weather_soup.find('div', attrs={'class': 'fact__temp-wrap'})
#     image_src = image_src.find('img', attrs={'class': 'icon'})['src']  # appropriate weather image
#
#     wind_speed_and_direction = weather_soup.find('div', attrs={'class': 'fact__props'})
#     try:
#         wind_speed = wind_speed_and_direction.find('span', attrs={'class': 'wind-speed'}).text  # wind speed
#         wind_direction = wind_speed_and_direction.find('abbr')['title']  # wind direction
#     except:
#         wind_speed = 'Штиль'
#         wind_direction = ''
#
#     humidity = weather_soup.find('div', attrs={'class': 'fact__humidity'})
#     humidity = humidity.find('div', attrs={'class': 'term__value'}).text  # humidity percentage
#
#     condition = weather_soup.find('div', attrs={
#         'class': 'link__condition'}).text  # condition comment (clear, windy etc.)
#
#     feels_like = weather_soup.find('div', attrs={'class': 'term__value'})
#     feels_like = feels_like.find('div', attrs={'class': 'temp'}).text  # feels like temperature
#
#     daylight_soup = soup.find('div', attrs={'class': 'sun-card__info'})
#
#     daylight_hours = daylight_soup.find('div', attrs={
#         'class': 'sun-card__day-duration-value'}).text  # daylight duration
#     sunrise = daylight_soup.find('div', attrs={'class': 'sun-card__sunrise-sunset-info_value_rise-time'}).text[-5:]
#     sunset = daylight_soup.find('div', attrs={'class': 'sun-card__sunrise-sunset-info_value_set-time'}).text[-5:]
#
#     # extended_weather_soup = soup.find('ul', attrs={'class': 'swiper-wrapper'})
#     # weather_time = extended_weather_soup.find('div', attrs={'class': 'fact__hour-label'}).text
#     # weather_temperature = extended_weather_soup.find('div', attrs={'class': 'fact__hour-temp'}).text
#
#     content = {
#         'temperature': temperature,
#         'image_src': image_src,
#         'wind_speed': wind_speed,
#         'wind_direction': wind_direction,
#         'humidity': humidity,
#         'condition': condition,
#         'feels_like': feels_like,
#         'daylight_hours': daylight_hours,
#         'sunrise': sunrise,
#         'sunset': sunset,
#     }
#     return content
#
#
# def get_extended_info(city_name):
#     """return the extended weather info of the current day"""
#     source = requests.get('https://yandex.ru/pogoda/' + city_name + '/details')
#     soup = BeautifulSoup(source.content, 'html.parser')
#     weather_table = soup.find('table', attrs={'class': 'weather-table'})
#     weather_rows = weather_table.find_all('tr', attrs={'class': 'weather-table__row'})
#
#     daypart_dict = dict()
#     count = 0
#     for row in weather_rows:
#         weather_daypart = row.find('div', attrs={'class': 'weather-table__daypart'}).text
#         weather_daypart_temp = row.find('div', attrs={'class': 'weather-table__temp'}).text
#         weather_daypart_condition = row.find('td', attrs={'class': 'weather-table__body-cell_type_condition'}).text
#         weather_daypart_wind = row.find('span', attrs={'class': 'weather-table__wind'}).text
#         weather_daypart_direction = row.find('abbr')['title']
#         temp_daypart_dict = {
#             'weather_daypart': weather_daypart,
#             'weather_daypart_temp': weather_daypart_temp,
#             'weather_daypart_condition': weather_daypart_condition,
#             'weather_daypart_wind': weather_daypart_wind,
#             'weather_daypart_direction': weather_daypart_direction
#         }
#         count += 1
#         part_num = str(count)
#         daypart_dict['part' + part_num] = temp_daypart_dict
#
#     return daypart_dict
#
