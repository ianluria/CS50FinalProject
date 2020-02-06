from app import db, login
import datetime
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Sales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, nullable=False)
    itemName = db.Column(db.String(255),  db.ForeignKey("items.itemName"), index=True, nullable=False)
    date = db.Column(db.Date, index=True, default=date.today, nullable=False)
    price = db.Column(db.String(64), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    shipping = db.Column(db.String(64), nullable=False)
    profit = db.Column(db.String(64), nullable=False)
    packaging = db.Column(db.String(64), nullable=True)
    payPalFees = db.Column(db.String(64))
    eBayFees = db.Column(db.String(64))
    refund = db.Column(db.Boolean)

    def __repr__(self):
        return '<Sales {}>'.format(self.username)

class Items(db.Model):
    itemName = db.Column(db.String(255), index=True, primary_key=True)
    username = db.Column(db.String(64), db.ForeignKey("user.username"), index=True, nullable=False)
    date = db.Column(db.Date, index=True, default=date.today, nullable=False)
    price = db.Column(db.String(64), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    sales = db.relationship("Sales", backref="item", lazy="dynamic")

    def __repr__(self):
        return '<Items {}>'.format(self.itemName)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    payPalFixed = db.Column(db.String(64), default=0)
    payPalPercent = db.Column(db.String(64), default=0)
    eBayPercent = db.Column(db.String(64), default=0)
    saleDisplayInfo = db.Column(db.Text)
    items = db.relationship("Items", backref="user", lazy="dynamic")

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def removeItem(self, item):
        if self.has_item(item):
            self.items.remove(item)

    def has_item(self, item):
        return self.items.filter(usersItem==item).count() > 0



@login.user_loader
def load_user(id):
    return User.query.get(int(id))