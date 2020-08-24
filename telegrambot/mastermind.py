from telegrambot.sub_mastermind import *


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


def get_daily(city_name, ):
    transliterated_city = transliterate_name(city_name)
    extended_info = get_extended_info(transliterated_city)
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


def get_start(first_name):
    """returns greeting and a short navigate information"""
    text = f'<b>Hello, {first_name} !\nWrite down your location</b> 🌏 \n\nFor more options use /help'
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


if __name__ == '__main__':
    print(get_daily('Питер'))
    # print(get_response('Питер'))
