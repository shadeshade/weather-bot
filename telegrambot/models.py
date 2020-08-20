# from app import db
#
#
#
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(32), unique=True, nullable=False)
#     chat_id = db.Column(db.Integer, unique=True, nullable=False)
#     city_name = db.Column(db.String(20), )
#     city_name2 = db.Column(db.String(20), )
#     city_name3 = db.Column(db.String(20), )
#
#     def __repr__(self):
#         return f"User('{self.username}', '{self.chat_id}', '{self.city_name}', '{self.city_name2}', '{self.city_name3}',)"
#
