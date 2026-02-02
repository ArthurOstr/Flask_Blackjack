import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy() 

class User(db.Model):
    __tablename__ = 'users'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # Game Stats
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    money = db.Column(db.Integer, default=1000)
    
    def __repr__(self):
        return f'<User {self.username}>'

def init_db(app):
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
