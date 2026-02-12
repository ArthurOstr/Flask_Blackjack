import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # Game Stats
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    money = db.Column(db.Integer, default=1000)

    # Relationship
    games = db.relationship("Game", backref="player", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


# State container
class Game(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    player_hand = db.Column(JSON, default=list)
    dealer_hand = db.Column(JSON, default=list)
    deck = db.Column(JSON, default=list)
    status = db.Column(db.String(20), default="active")
    bet = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"Game {self.id} | Status {self.status}>"


def init_db(app):
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
