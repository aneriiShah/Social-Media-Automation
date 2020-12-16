from app import db
from datetime import datetime

class AccessToken(db.Model):
    __tablename__ = 'access_token'
    social_id = db.Column(db.String(120), primary_key=True, nullable=False)
    name = db.Column(db.String(120))
    user_id = db.Column(db.String(120), nullable=False)
    medium = db.Column(db.String(80), primary_key=True,nullable=False)
    token = db.Column(db.String(320), unique=True, nullable=False)
    token_2 = db.Column(db.String(320))
    exp_dt = db.Column(db.DateTime)
