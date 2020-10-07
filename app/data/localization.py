buttons = {
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

inline_buttons = {
    'strong wind': {'en': 'Strong wind', 'ru': 'Сильный ветер'},
    'hailstorm': {'en': 'Hailstorm', 'ru': 'Град'},
    'hurricane': {'en': 'Hurricane', 'ru': 'Ураган'},
    'thunderstorm': {'en': 'Thunderstorm', 'ru': 'Гроза'},
    'rain': {'en': 'Rain', 'ru': 'Дождь'},
    'heavy rain': {'en': 'Heavy rain', 'ru': 'Ливень'},
    'fog': {'en': 'Fog', 'ru': 'Туман'},
    'intense heat': {'en': 'Intense heat', 'ru': 'Сильная жара'},
    'manually': {'en': 'Manually', 'ru': 'Вручную'},
    'positive temperature': {'en': 'Positive temperature', 'ru': 'Положительная температура'},
    'negative temperature': {'en': 'Negative temperature', 'ru': 'Отрицательная температура'},
    'wind speed': {'en': 'Wind speed', 'ru': 'Скорость ветра'},
    'humidity': {'en': 'Humidity', 'ru': 'Влажность'},
    'all phenomena': {'en': 'All phenomena', 'ru': 'Все события'},
    'set time': {'en': 'Set time', 'ru': 'Изменить время'},
    'back': {'en': '↩ Back', 'ru': '↩ Назад'},
    'remove all daily': {'en': 'Remove all', 'ru': 'Удалить все'},
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
        'en': 'Select phenomena and time at which you would like to receive notifications',
        'ru': 'Выберите события и время в которое вы хотели бы получать оповещения'},
    'phenomena manually intro': {
        'en': 'Here you can configure phenomena in more detail',
        'ru': 'Здесь вы можете настроить события более детально'},
    'num expected': {
        'en': 'Enter a number to set the temperature',
        'ru': 'Чтобы установить температуру, введите число'},
    'num pos expected': {
        'en': 'The number must be positive',
        'ru': 'Число должно быть положительным'},
    'num neg expected': {
        'en': 'The number must be negative',
        'ru': 'Число должно быть отрицательным'},
    'cancel': {'en': 'Canceled', 'ru': 'Отменено'},
    'phenomena temp set': {
        'en': 'I will notify you if a certain temperature is expected tomorrow',
        'ru': 'Я уведомлю вас если завтра будет ожидаться установленная температура'},
    'phenomenon set del': {'en': 'The phenomenon', 'ru': 'Cобытие '},
    'phenomenon set': {'en': 'was set', 'ru': 'добавлено'},
    'ph manually set': {'en': 'was set at', 'ru': 'было установлено на'},
    'phenomenon delete': {'en': 'has been deleted', 'ru': 'удалено'},
    'phenomenon tomorrow': {'en': 'Expected tomorrow:', 'ru': 'Завтра ожидается:'},
    'phenomenon': {'en': 'Phenomenon', 'ru': 'Событие'},
    'all tick': {'en': 'All phenomena are chosen', 'ru': 'Все события отмечены'},
    'all untick': {'en': 'All phenomena are removed', 'ru': 'Все события отключены'},
    'phenomena time': {'en': 'Set the time you want to receive phenomenon information',
                       'ru': 'Выберите время в которое вы хотите получать оповещение'},
    'city intro': {
        'en': 'Here you can change the city. To do this, just enter the name of the city',
        'ru': 'Здесь вы можете изменить свой город. Для этого просто введите название города'},
    'city added': {'en': 'The city has been changed', 'ru': 'Ваш город добавлен'},
    'city fail': {'en': 'I do not know this city', 'ru': 'Я не знаю такого города'},
    'lang intro': {'en': 'Here you can choose your language',
                   'ru': 'Здесь вы можете выбрать необходимый язык'},
    'lang chosen': {'en': 'English has been chosen',
                    'ru': 'Русский язык выбран'},
    'help intro': {
        'en': '<b>Hello, below is a list of buttons and their functions with which I can work.</b>'
              '\n\n<b>Weather now:</b>\nGet information about the current weather.'
              '\n\n<b>For tomorrow:</b>\nGet information about the weather for tomorrow.'
              '\n\n<b>For a week:</b>\nGet weather information for the next 7 days.'
              '\n\n<b>Daily:</b>\nSet daily time you want to receive weather information.'
              '\n\n<b>Phenomena:</b>\nSelect phenomena and time at which you would like to receive notification of'
              ' an upcoming phenomenon.'
              '\n\n<b>City:</b>\nChoose your city.'
              '\n\n<b>Language:</b>\nChoose your language.'
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
              '\n\nТакже вы можете ввести название города и получить информацию, не меняя ранее установленный город.'
    },
}

# weather info
info = {
    'en': [
        'Try again', 'Now', 'Wind', 'Feels like', 'Daylight hours', 'Sunrise - Sunset', 'on', 'Calm',
        'Weather for 7 days', 'Settings', 'm/s', 'Temperature'
    ],
    'ru': [
        'Попробуйте еще раз', 'Сейчас', 'Ветер', 'Ощущается как', 'Световой день', 'Восход - Закат', 'на', 'Штиль',
        'Погода на 7 дней', 'Настройки', 'м/с', 'Температура'
    ],
}


ph_info = {
    'strong wind': {'en': 'Strong wind', 'ru': 'Сильный ветер'},
    'hailstorm': {'en': 'Hailstorm', 'ru': 'Град'},
    'hurricane': {'en': 'Hurricane', 'ru': 'Ураган'},
    'thunderstorm': {'en': 'Thunderstorm', 'ru': 'Гроза'},
    'rain': {'en': 'Rain', 'ru': 'Дождь'},
    'heavy rain': {'en': 'Heavy rain', 'ru': 'Сильный дождь'},
    'intense heat': {'en': 'Intense heat', 'ru': 'Сильная жара'},
    'positive temperature': {'en': 'Positive temperature', 'ru': 'Положительная температура'},
    'negative temperature': {'en': 'Negative temperature', 'ru': 'Отрицательная температура'},
    'wind speed': {'en': 'Wind speed', 'ru': 'Скорость ветра'},
    'humidity': {'en': 'Humidity', 'ru': 'Влажность'},

}
