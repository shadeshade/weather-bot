from app import db


class User(db.Model):
    # __tablename__ = "UsersTable"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    chat_id = db.Column(db.Integer, unique=True, nullable=False)
    city_name = db.Column(db.String(20), )
    reminder_time = db.relationship('ReminderTime', backref='telegram_user', lazy=True)
    phenomena_time = db.relationship('PhenomenaTime', backref='telegram_user', lazy=True)
    language = db.Column(db.String(2))

    def __repr__(self):
        return f"User('{self.username}', '{self.chat_id}', '{self.city_name}')"


class ReminderTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hours = db.Column(db.Integer)
    minutes = db.Column(db.Integer)
    job_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"ReminderTime({self.hours}:{self.minutes})"


class PhenomenaTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phenomena = db.Column(db.String)
    hours = db.Column(db.Integer)
    minutes = db.Column(db.Integer)
    job_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"ReminderTime({self.hours}:{self.minutes})"


"""
  '{self.chat_id}','{self.city_name}',
user1 = User(username='fea', chat_id=142142412, city_name='fdadfafa', )
"""
