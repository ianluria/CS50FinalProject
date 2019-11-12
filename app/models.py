from app import db, login
import datetime
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Sales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    item = db.Column(db.String(255),  db.ForeignKey("items.item"), index=True)
    date = db.Column(db.Date, index=True, default=date.today)
    price = db.Column(db.Float(2))
    quantity = db.Column(db.Integer)
    shipping = db.Column(db.Float(2))

    def __repr__(self):
        return '<Sales {}>'.format(self.username)


class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    item = db.Column(db.String(255), index=True, unique=True)
    date = db.Column(db.Date, index=True, default=date.today)
    price = db.Column(db.Float(2))
    quantity = db.Column(db.Integer)
    sales = db.relationship("Sales", backref="item1", lazy="dynamic")

    def __repr__(self):
        return '<Items {}>'.format(self.username)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User ()>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))