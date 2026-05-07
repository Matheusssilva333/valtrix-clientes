from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roblox_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(100))
    display_name = db.Column(db.String(100))
    avatar_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(50))
    item_id = db.Column(db.String(50))
    item_name = db.Column(db.String(200))
    item_price = db.Column(db.Float)
    buyer_uid = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending') # pending, confirmed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)

class Affiliate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    owner_id = db.Column(db.String(50))
    total_sales = db.Column(db.Integer, default=0)
    total_commission = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
