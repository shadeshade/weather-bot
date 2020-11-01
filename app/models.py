from app import db
from app import logger


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32))
    chat_id = db.Column(db.Integer, nullable=False)
    city_name = db.Column(db.String(20), )
    reminder_time = db.relationship('ReminderTime', backref='telegram_user', lazy=True)
    phenomenon_time = db.relationship('PhenomenonTime', backref='telegram_user', lazy=True)
    phenomenon = db.relationship('Phenomenon', backref='telegram_user', lazy=True)
    language = db.Column(db.String(2))

    def __repr__(self):
        return f"User('{self.username}', '{self.chat_id}', '{self.city_name}')"

    @staticmethod
    def get_user_data(message):
        chat_id = message.chat.id
        user = User.query.filter_by(chat_id=chat_id).first()
        username = message.from_user.first_name
        try:
            lang = user.language
        except AttributeError as e:
            logger.warning(e)
            lang = message.from_user.language_code
        try:
            city_name = user.city_name
        except AttributeError as e:
            logger.warning(e)
            city_name = None

        data_dict = {'user': user, 'username': username, 'city_name': city_name, 'chat_id': chat_id, 'lang': lang}
        return data_dict


# todo: Merge tables ReminderTime and PhenomenonTime into one
# todo: make job_ib into string type
class ReminderTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hours = db.Column(db.Integer)
    minutes = db.Column(db.Integer)
    job_id = db.Column(db.String, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"ReminderTime({self.hours}:{self.minutes})"


class PhenomenonTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hours = db.Column(db.Integer)
    minutes = db.Column(db.Integer)
    job_id = db.Column(db.String, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"PhenomenonTime({self.hours}:{self.minutes})"


class Phenomenon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phenomenon = db.Column(db.String)
    value = db.Column(db.Integer, default=None)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"\nPhenomenon {self.phenomenon} is set to {self.value}"
        # return f"Phenomenon{self.phenomenon}"


# Better to move 'value' field in Phenomenon model (and get rid of PhenomenonManually)
# but it requires a lot of changes across the code base
# class PhenomenonManually(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     phenomenon = db.Column(db.String)
#     value = db.Column(db.Integer)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#
#     def __repr__(self):
#         return f"Phenomenon{self.phenomenon} is set to {self.value}"