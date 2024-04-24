from flask_login import UserMixin
from config import db


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    text = db.Column(db.Text, nullable=False)
    author = db.Column(
        db.Integer, db.ForeignKey('authors.id'), nullable=False)


class Author(db.Model, UserMixin):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    posts = db.relationship('Post', backref='user_post')
