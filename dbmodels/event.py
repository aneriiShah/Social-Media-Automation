from app import db
from datetime import datetime

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(120), db.ForeignKey('access_token.social_id'), nullable=False)
    medium = db.Column(db.String(120), nullable=False)
    text= db.Column(db.String(120), nullable=False)
    req_dt = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    sch_dt =  db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')
    active = db.Column(db.Boolean,default=True)
    notifications = db.Column(db.Boolean)
    filename = db.Column(db.String(120))
    remarks = db.Column(db.String)