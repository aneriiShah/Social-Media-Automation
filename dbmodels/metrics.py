from app import db
from datetime import datetime

class Metrics(db.Model):
    __tablename__ = 'metrics'
    social_id = db.Column(db.String(120), db.ForeignKey('access_token.social_id'), nullable=False, primary_key=True)
    datetime =  db.Column(db.DateTime, nullable=False, primary_key=True)
    medium = db.Column(db.String(120), nullable=False)
    metrics= db.Column(db.String(120), nullable=False, primary_key=True)
    value = db.Column(db.String, nullable=False)
    remarks = db.Column(db.String)