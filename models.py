from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock = db.Column(db.String(100), nullable=False)
    date_time = db.Column(db.String(25), nullable=False)
    bias = db.Column(db.String(10), nullable=False)
    position_size = db.Column(db.Numeric(10, 2), nullable=False)
    entry_reason = db.Column(db.String(255), nullable=False)
    exit_reason = db.Column(db.String(255), nullable=False)
    outcome = db.Column(db.String(20), nullable=False)
    rr = db.Column(db.Numeric(10, 2), nullable=False)
    notes = db.Column(db.String(255))
    emotion = db.Column(db.String(100), nullable=False)
    trading_plan = db.Column(db.String(10), nullable=False)
    balance = db.Column(db.Numeric(10, 2), nullable=False)
    pnl = db.Column(db.Numeric(10, 2), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ForeignKey

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_premium = db.Column(db.Boolean, default=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    trades = db.relationship('Trade', backref='user', lazy=True)  # Relationship