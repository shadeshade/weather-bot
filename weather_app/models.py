from weather_app import db
from weather_app import logger


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32))
    chat_id = db.Column(db.Integer, nullable=False)
    city_name = db.Column(db.String(20), )
    reminder_time = db.relationship('ReminderTime', backref='telegram_user', lazy=True)
    phenomenon = db.relationship('Phenomenon', backref='telegram_user', lazy=True)
    language = db.Column(db.String(2))

    def __repr__(self):
        return f"User('{self.username}', '{self.chat_id}', '{self.city_name}')"

    @staticmethod
    def get_or_create_user_data(message):
        chat_id = message.chat.id
        user = User.query.filter_by(chat_id=chat_id).first()
        try:
            username = message.from_user.first_name
        except AttributeError as err:
            logger.warning(f'Couldn\'t get first name from Telegram API, error: {err}')
            username = ''

        if not user:
            city_name = None
            lang = message.from_user.language_code
            user = User(username=username, chat_id=chat_id, language=lang)
            db.session.add(user)
            db.session.commit()
        else:
            city_name = user.city_name
            lang = user.language

        return {'user': user, 'username': username, 'city_name': city_name, 'chat_id': chat_id, 'lang': lang}


class ReminderTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_phenomenon = db.Column(db.Boolean, default=False)
    hours = db.Column(db.Integer)
    minutes = db.Column(db.Integer)
    job_id = db.Column(db.String, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"ReminderTime {self.hours}:{self.minutes} (is phenomenon - {self.is_phenomenon})\n"


class Phenomenon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phenomenon = db.Column(db.String)
    is_manually = db.Column(db.Boolean, default=False)
    value = db.Column(db.Integer, default=None)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Phenomenon {self.phenomenon} is set to {self.value}\n"
