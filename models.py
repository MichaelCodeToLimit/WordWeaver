from datetime import datetime
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    difficulty = db.Column(db.String(10), default='medium')
    time_limit = db.Column(db.Integer)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    final_score = db.Column(db.Integer, default=0)

class WordChain(db.Model):
    __tablename__ = 'word_chains'
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id', ondelete='CASCADE'))
    word = db.Column(db.String(100), nullable=False)
    previous_word = db.Column(db.String(100))
    points = db.Column(db.Integer, default=0)
    player_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)