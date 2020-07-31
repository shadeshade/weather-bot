from telebot.sub_mastermind import *


def get_response(city_name):
    '''basic function'''
    transliterated_city = transliterate_name(city_name)
    current_temperature = get_temperature(transliterated_city)
    return current_temperature


def start_command(first_name):
    '''returns greeting and a short navigate information'''
    welcome_text = 'Hello, ' + first_name + ' !\n'
    text = welcome_text + 'Write down your location 🌏 \n' \
                          'For more options use /help'
    return text


def help_command():
    '''returns commands list'''
    text = '/start:\nStart bot interaction.\n\n' \
           '/daily:\nSet daily time you want to receive weather information. More than one city addition is available\n\n' \
           '/remove_daily:\nChoose the city to remove from your daily info.\n\n' \
           '/reminder:\nSet reminder about the incoming event you want. E.g. receive a message that rain' \
           ' is expected in two days\n\n' \
           '/remove_reminder:\nChoose the reminder name to remove from your reminder list.'
    return text


if __name__ == '__main__':
    print(get_response('Питер'))
