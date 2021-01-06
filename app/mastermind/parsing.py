import requests
from bs4 import BeautifulSoup

from app import logger
from app.data.localization import info


def get_weather_info(city_name, lang):
    """return the current weather info"""
    url_ending = 'ru' if lang == 'ru' else 'com'
    source = requests.get(f'https://yandex.{url_ending}/pogoda/{city_name}')

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
        wind_speed_and_direction = f"{wind_speed} {wind_direction}"
    except AttributeError as e:
        logger.warning(f'No wind\n{repr(e)}')
        wind_speed_and_direction = info[lang][7]

    humidity = weather_soup.find('div', attrs={'class': 'fact__humidity'})
    humidity = humidity.find('div', attrs={'class': 'term__value'}).text  # humidity percentage

    condition = weather_soup.find('div', attrs={
        'class': 'link__condition'}).text  # condition comment (clear, windy etc.)

    feels_like = weather_soup.find('div', attrs={'class': 'link__feelings fact__feelings'})
    feels_like = feels_like.find('div', attrs={'class': 'temp'}).text  # feels like temperature

    daylight_soup = soup.find('div', attrs={'class': 'sun-card__info'})
    daylight_hours = daylight_soup.find('div', attrs={
        'class': 'sun-card__day-duration-value'}).text  # daylight duration
    sunrise = daylight_soup.find('div', attrs={'class': 'sun-card__sunrise-sunset-info_value_rise-time'}).text[-5:]
    sunset = daylight_soup.find('div', attrs={'class': 'sun-card__sunrise-sunset-info_value_set-time'}).text[-5:]

    response_message = {
        'header': header,
        'temperature': temperature,
        'wind_speed_and_direction': wind_speed_and_direction,
        'humidity': humidity,
        'condition': condition,
        'feels_like': feels_like,
        'daylight_hours': daylight_hours,
        'sunrise': sunrise,
        'sunset': sunset,
    }
    return response_message


def get_day_info(weather_rows, unit, lang):
    """Parse day parts of the extended info"""
    daypart_dict = dict()
    row_count = 0
    for row in weather_rows:
        weather_daypart = row.find('div', attrs={'class': 'weather-table__daypart'}).text
        weather_daypart_temp = row.find('div', attrs={'class': 'weather-table__temp'}).text
        weather_daypart_humidity = row.find('td', attrs={
            'class': 'weather-table__body-cell weather-table__body-cell_type_humidity'}).text
        weather_daypart_condition = row.find('td', attrs={'class': 'weather-table__body-cell_type_condition'}).text
        try:
            weather_daypart_wind = row.find('span', attrs={'class': 'weather-table__wind'}).text
            weather_unit = unit
            weather_daypart_direction = row.find('abbr', attrs={'class': 'icon-abbr'}).text
            wind_speed_and_direction = f'{weather_daypart_wind} {weather_unit}, {weather_daypart_direction}'
        except AttributeError as e:
            logger.warning(f'No wind\n{repr(e)}')
            wind_speed_and_direction = info[lang][7]

        temp_daypart_dict = {
            'weather_daypart': weather_daypart,
            'weather_daypart_temp': weather_daypart_temp,
            'weather_daypart_humidity': weather_daypart_humidity,
            'weather_daypart_condition': weather_daypart_condition,
            'wind_speed_and_direction': wind_speed_and_direction,
        }
        row_count += 1
        daypart_dict['part' + str(row_count)] = temp_daypart_dict
    return daypart_dict


def _get_extended_info_soup(city_name, lang):
    url_ending = 'ru' if lang == 'ru' else 'com'
    source = requests.get(f'https://yandex.{url_ending}/pogoda/{city_name}/details')

    soup = BeautifulSoup(source.content, 'html.parser')
    weather_unit = info[lang][10]
    return soup, weather_unit


def _get_extended_info_for_day(soup, weather_table, weather_unit, lang):
    weather_city = soup.find('h1', attrs={'class': 'title title_level_1 header-title__title'}).text
    weather_city = weather_city.split()[-1]

    daylight_soup = weather_table.find('div', attrs={'class': 'forecast-details__right-column'})
    daylight_hours = daylight_soup.find('dl', attrs={
        'class': 'sunrise-sunset__description sunrise-sunset__description_value_duration'})
    daylight_hours = daylight_hours.find('dd', attrs={
        'class': 'sunrise-sunset__value'}).text  # daylight duration
    sunrise = daylight_soup.find('dl', attrs={
        'class': 'sunrise-sunset__description sunrise-sunset__description_value_sunrise'}).text[-5:]
    sunset = daylight_soup.find('dl', attrs={
        'class': 'sunrise-sunset__description sunrise-sunset__description_value_sunset'}).text[-5:]

    weather_day = weather_table.find('strong', attrs={'class': 'forecast-details__day-number'}).text
    weather_month = weather_table.find('span', attrs={'class': 'forecast-details__day-month'}).text
    weather_date = f'{weather_day} {weather_month}'
    weather_rows = weather_table.find_all('tr', attrs={'class': 'weather-table__row'})

    daypart_dict = get_day_info(weather_rows, weather_unit, lang)
    daypart_dict['weather_date'] = weather_date
    daypart_dict['weather_city'] = weather_city
    daypart_dict['daylight_hours'] = daylight_hours
    daypart_dict['sunrise'] = sunrise
    daypart_dict['sunset'] = sunset

    return daypart_dict
    

def get_extended_info_for_week(city_name, lang):
    """return the extended weather info of the current day for daily cast.
    Handling 'for a week' button
    """
    soup, weather_unit = _get_extended_info_soup(city_name, lang)

    days_dict = dict()

    weather_tables = soup.find_all('div', attrs={'class': 'card'})[2:]
    for day_count, weather_day in enumerate(weather_tables):
        if day_count >= 7:  # output 7 days for the button 'for a week'
            break

        daypart_dict = _get_extended_info_for_day(soup, weather_day, weather_unit, lang)
        days_dict['day' + str(day_count)] = daypart_dict

    try:
        days_dict['weather_city'] = days_dict['day0']['weather_city']
    except KeyError:
        days_dict['weather_city'] = ''

    return days_dict


def get_extended_info(city_name, command, lang):
    """return the extended weather info of the current day for daily cast.
    Handling 'daily', 'tomorrow', 'today' buttons
    """
    soup, weather_unit = _get_extended_info_soup(city_name, lang)

    if command == 'daily':  # button daily
        weather_table = soup.find('div', attrs={'class': 'card'})
    elif command == 'tomorrow':  # button tomorrow
        weather_table = soup.find_all('div', attrs={'class': 'card'})[2]
    else:
        weather_table = soup.find_all('div', attrs={'class': 'card'})[0]

    daypart_dict = _get_extended_info_for_day(soup, weather_table, weather_unit, lang)
    return daypart_dict
