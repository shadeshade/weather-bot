button_names = {
    'weather now': {'en': '🧙🏻‍♀ Weather now', 'ru': '🧙🏻‍♀ Погода сейчас'},
    'for tomorrow': {'en': '🧙🏼 For tomorrow', 'ru': '🧙🏼 На завтра'},
    'for a week': {'en': '🧙🏿‍♂ For a week', 'ru': '🧙🏿‍♂ На неделю'},
    'settings': {'en': '🔮 Settings', 'ru': '🔮 Настройки'},
    'daily': {'en': '📋 Daily', 'ru': '📋 По графику'},
    'phenomena': {'en': '🌩 Phenomena', 'ru': '🌩 События'},
    'city': {'en': '🌆 City', 'ru': '🌆 Город'},
    'language': {'en': '🇬🇧 Language', 'ru': '🇷🇺 Язык'},
    'info': {'en': '👨🏻‍🔬 Info', 'ru': '👨🏻‍🔬 Инфо'},
    'help': {'en': '⁉ Help', 'ru': '⁉ Помощь'},
    'menu': {'en': '↩ Menu', 'ru': '↩ Меню'},
}

# Phenomenon buttons and localized information about various phenomena
phenomenon_button_names = {
    'strong wind': {'en': 'Strong wind', 'ru': 'Сильный ветер'},
    'hurricane': {'en': 'Hurricane', 'ru': 'Ураган'},
    'intense heat': {'en': 'Intense heat', 'ru': 'Сильная жара'},

    'hailstorm': {'en': 'Hailstorm', 'ru': 'Град'},
    'thunderstorm': {'en': 'Thunderstorm', 'ru': 'Гроза'},
    'rain': {'en': 'Rain', 'ru': 'Дождь'},
    'heavy rain': {'en': 'Heavy rain', 'ru': 'Ливень'},

    'temperature more': {'en': 'Temperature is more', 'ru': 'Температура больше'},
    'temperature less': {'en': 'Temperature is less', 'ru': 'Температура меньше'},
    'wind speed': {'en': 'Wind speed', 'ru': 'Скорость ветра'},
    'humidity': {'en': 'Humidity', 'ru': 'Влажность'},

    'manually': {'en': 'Manually', 'ru': 'Вручную'},
    'all phenomena': {'en': 'All phenomena', 'ru': 'Все события'},
    'set time': {'en': 'Set time', 'ru': 'Изменить время'},
    'back': {'en': '↩ Back', 'ru': '↩ Назад'},
    'remove all': {'en': 'Remove all', 'ru': 'Удалить все'},
}

hints = {
    'start msg1': {'en': '<b>Welcome, ', 'ru': '<b>Добро пожаловать, '},
    'start msg2': {
        'en': ' !\nPlease, type your location</b> 🌏 \n\nFor more info use /help',
        'ru': ' !\nНапишите название своего города</b> 🌏 \n\nДля дополнительной информации используйте /help'},
    'no city': {'en': 'No city was set up. Please, type the name of your city',
                'ru': 'Город не был выбран. Пожалуйста, введите название города'},
    'time daily': {'en': 'Set daily time you want to receive weather information',
                   'ru': 'Выбирите время, в которое вы бы хотели получать уведомления'},
    'menu': {'en': 'Main menu', 'ru': 'Главное меню'},
    'schedule set': {'en': 'The schedule was set at', 'ru': 'График был установлен на'},
    'schedule delete': {
        'en': 'The schedule for this time has been deleted',
        'ru': 'График на это время был удален'},
    'phenomena intro': {
        'en': 'Select phenomena and time at which you would like to receive notifications of '
              'the upcoming phenomena next day.',
        'ru': 'Выберите события и время в которое вы хотели бы получать оповещения '
              'о предстоящих событиях на следующий день.'},
    'phenomena manually intro': {
        'en': 'Here you can configure phenomena in more detail.',
        'ru': 'Здесь вы можете настроить события более детально.'},
    'remove manually': {
        'en': 'All phenomena removed.',
        'ru': 'Все события удалены.'},
    'how to del': {
        'en': 'Enter zero to delete.',
        'ru': 'Введите ноль, чтобы удалить.'},
    'num expected': {
        'en': 'Enter a number to set the value.',
        'ru': 'Введите число, чтобы установить значение.'},
    'num pos expected': {
        'en': 'The number must be positive',
        'ru': 'Число должно быть положительным'},
    'cancel': {'en': 'Canceled', 'ru': 'Отменено'},
    'phenomena temp set': {
        'en': 'I will notify you if tomorrow the value you set is expected.',
        'ru': 'Я сообщу вам, если завтра ожидается установленное вами значение.'},
    'phenomenon set del': {'en': 'The phenomenon', 'ru': 'Cобытие '},
    'phenomenon set': {'en': 'was set', 'ru': 'добавлено'},
    'ph manually set': {'en': 'was set at', 'ru': 'было установлено на'},
    'phenomenon delete': {'en': 'has been deleted', 'ru': 'удалено'},
    'phenomenon tomorrow': {'en': 'Expected tomorrow:', 'ru': 'Завтра ожидается:'},
    'phenomenon': {'en': 'Phenomenon', 'ru': 'Событие'},
    'all tick': {'en': 'All phenomena are chosen', 'ru': 'Все события отмечены'},
    'all untick': {'en': 'All phenomena are removed', 'ru': 'Все события удалены'},
    'phenomena time': {'en': 'Set the time you want to receive phenomenon information',
                       'ru': 'Выберите время в которое вы хотите получать оповещения'},
    'city intro': {
        'en': 'Here you can change the city. To do this, just enter the name of the city',
        'ru': 'Здесь вы можете изменить свой город. Для этого просто введите название города'},
    'city added': {'en': 'The city has been changed', 'ru': 'Ваш город добавлен'},
    'city fail': {'en': 'I do not know this city', 'ru': 'Я не знаю такого города'},
    'lang intro': {'en': 'Here you can choose your language',
                   'ru': 'Здесь вы можете выбрать необходимый язык'},
    'lang chosen': {'en': 'English has been chosen',
                    'ru': 'Русский язык выбран'},
    'set info': {'en': 'No data', 'ru': 'Нет данных'},
    'help intro': {
        'en': '<b>Hello, below is a list of buttons and their functions with which I can work.</b>'
              '\n\n<b>Weather now:</b>\nGet information about the current weather.'
              '\n\n<b>For tomorrow:</b>\nGet information about the weather for tomorrow.'
              '\n\n<b>For a week:</b>\nGet weather information for the next 7 days.'
              '\n\n<b>Daily:</b>\nSet daily time you want to receive weather information.'
              '\n\n<b>Phenomena:</b>\nSelect phenomena and time at which you would like to receive notifications of'
              ' an upcoming phenomenon next day.'
              '\n\n<b>City:</b>\nChoose your city.'
              '\n\n<b>Language:</b>\nChoose your language.'
              '\n\n<b>Info:</b>\nDisplays a message with the phenomena and times you chose.'
              '\n\nAlso you can enter the name of the city and get information without changing the previously set '
              'city',
        'ru': '<b>Привет, ниже приведен список кнопок и их фунции, с которыми я умею работать.</b>'
              '\n\n<b>Погода сейчас:</b>\nПолучить информацию о текущей погоде.'
              '\n\n<b>На завтра:</b>\nПолучить информацию о погоде на завтра.'
              '\n\n<b>На неделю:</b>\nПолучить информацию о погоде на следующие 7 дней.'
              '\n\n<b>По графику:</b>\nУстановить время на каждый день, в которое вы хотели бы получать информацию'
              ' о погоде.'
              '\n\n<b>События:</b>\nВыбрать события и время получения оповещения о предстоящем событии.'
              '\n\n<b>Город:</b>\nВыберите ваш город.'
              '\n\n<b>Язык:</b>\nВыберите ваш язык.'
              '\n\n<b>Инфо:</b>\nОтображает сообщение с выбранными вами событиями и временем.'
              '\n\nТакже вы можете ввести название города и получить информацию, не меняя ранее установленный город.'
    },
}

# weather info
info = {
    'en': [
        'Try again', 'Now', 'Wind', 'Feels like', 'Daylight hours', 'Sunrise - Sunset', 'on', 'Calm',
        'Weather for 7 days', 'Settings', 'm/s', 'Temperature', 'Time', 'not set'
    ],
    'ru': [
        'Попробуйте еще раз', 'Сейчас', 'Ветер', 'Ощущается как', 'Световой день', 'Восход - Закат', 'на', 'Штиль',
        'Погода на 7 дней', 'Настройки', 'м/с', 'Температура', 'Время', 'не задано'
    ],
}

# check if a phenomenon has an alias for returning the condition
phenomenon_aliases = {
    'hailstorm': {'en': ['hail', 'hailstorm', 'thunderstorm with hail'],
                  'ru': ['град', 'гроза с градом']},
    'thunderstorm': {'en': ['thunderstorm', 'thunderstorm with hail', 'thunderstorm with rain'],
                     'ru': ['гроза', 'гроза с градом', 'дождь с грозой']},
    'rain': {'en': ['rain', 'moderate rain', 'wet snow'],
             'ru': ['дождь', 'умеренно сильный дождь', 'дождь со снегом']},
    'heavy rain': {
        'en': ['thunderstorm with rain', 'heavy rain', 'continuous-heavy-rain', 'showers', 'thunderstorm with hail'],
        'ru': ['дождь с грозой', 'ливень', 'длительный сильный дождь', 'ливень', 'гроза с градом', 'сильный дождь']},
}
