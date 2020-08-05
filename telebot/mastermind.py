from telebot.sub_mastermind import *


def get_response(city_name):
    '''basic function'''
    transliterated_city = transliterate_name(city_name)

    try:
        weather_info = get_weather_info(transliterated_city)
    except:
        return 'try again'

    # TODO: get the current weather picture
    # photo_src = get_image(transliterated_city)
    # photo_src = 'https://uraloved.ru/images/mesta/perm-krai/kama/kama-1.jpg'
    # res = {
    #     'current_temperature': current_temperature,
    #     'photo_src': photo_src
    # }


    response_message = f'temp: {weather_info["temperature"]}\n' \
                       f'wind_speed: {weather_info["wind_speed"]}\n' \
                       f'humidity: {weather_info["humidity"]}\n' \
                       f'condition: {weather_info["condition"]}\n' \
                       f'feels_like: {weather_info["feels_like"]}\n' \
                       f'daylight_hours: {weather_info["daylight_hours"]}\n' \
                       f'sunrise: {weather_info["sunrise"]}\n' \
                       f'sunset: {weather_info["sunset"]}\n'

    return response_message


def start_command(first_name):
    '''returns greeting and a short navigate information'''
    welcome_text = 'Hello, ' + first_name + ' !\n'
    text = welcome_text + 'Write down your location 🌏 \n' \
                          'For more options use /help'
    return text


def help_command():
    '''returns commands list'''
    text = '/start:\nStart bot interaction.\n\n' \
           '/daily:\nSet daily time you want to receive weather information. More than one city addition is ' \
           'available\n\n' \
           '/remove_daily:\nChoose the city to remove from your daily info.\n\n' \
           '/reminder:\nSet reminder about the incoming event you want. E.g. receive a message that rain' \
           ' is expected in two days\n\n' \
           '/remove_reminder:\nChoose the reminder name to remove from your reminder list.'
    return text


if __name__ == '__main__':
    print(get_response('Питер'))
