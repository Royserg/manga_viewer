from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Set many to many relationships - helper table
subs = db.Table('subs',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('manga_id', db.Text, db.ForeignKey('manga.id'), primary_key=True)
)

class Manga(db.Model):
    __tablename__ = "manga"
    id = db.Column(db.Text, autoincrement=False, primary_key=True)
    alias = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    image = db.Column(db.String)
    last_chap_date = db.Column(db.Numeric)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    subscriptions = db.relationship("Manga", secondary=subs, backref="subscribers", lazy=True)
