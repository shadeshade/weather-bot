import os

# SQLALCHEMY_DATABASE_URI = 'sqlite:///C:\\Users\\shade\\Desktop\\projects\\weather_bot\\bot.db'

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False