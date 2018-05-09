from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# Set many to many relationships - helper table
subs = db.Table('subs',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('manga_id', db.String(150), db.ForeignKey('manga.id'), primary_key=True)
)

class Manga(db.Model):
    __tablename__ = "manga"
    id = db.Column(db.String(150), autoincrement=False, primary_key=True)
    alias = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(200))
    last_chap_date = db.Column(db.Numeric)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(80))
    subscriptions = db.relationship("Manga", secondary=subs, 
                    backref=db.backref("subscribers", lazy='dynamic'))

