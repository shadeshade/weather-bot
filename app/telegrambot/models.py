from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    chat_id = db.Column(db.Integer, unique=True, nullable=False)
    city_name = db.Column(db.String(20), )
    reminder_time = db.relationship('ReminderTime', backref='telegram_user', lazy=True)
    phenomenon_time = db.relationship('PhenomenonTime', backref='telegram_user', lazy=True)
    phenomenon = db.relationship('Phenomenon', backref='telegram_phenomenon', lazy=True)
    language = db.Column(db.String(2))

    def __repr__(self):
        return f"User('{self.username}', '{self.chat_id}', '{self.city_name}')"


class ReminderTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hours = db.Column(db.Integer, nullable=False)
    minutes = db.Column(db.Integer, nullable=False)
    job_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"ReminderTime({self.hours}:{self.minutes})"


class PhenomenonTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hours = db.Column(db.Integer, nullable=False)
    minutes = db.Column(db.Integer, nullable=False)
    job_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"PhenomenonTime({self.hours}:{self.minutes})"


class Phenomenon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phenomenon = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Phenomenon({self.phenomenon})"


class PhenomenonManually(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phenomenon = db.Column(db.String, nullable=False)
    value = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Phenomenon{self.phenomenon} is set to {self.value}"
