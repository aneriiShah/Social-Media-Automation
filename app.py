from flask import Flask,request,redirect, jsonify,render_template,make_response,render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta
from utils.insta_auto_settings import instaAutoSettings
import requests
from os.path import join, dirname
from dotenv import load_dotenv
import os
import pandas as pd
import uuid
# from instabot import Bot


import atexit
from apscheduler.schedulers.background import BackgroundScheduler

# Create .env file path
dotenv_path = join(dirname(__file__), '.env')

# load file from the path
load_dotenv(dotenv_path)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

from scheduler import Scheduler
from media.linkedIn import LinkedInBot
from media.facebook import FaceBookBot
from media.twitter import TwitterBot

from utils.s3Helper import S3Helper

# Flask Manager Commands
@app.cli.command("create_db")
def create_db():
    from dbmodels.accesstoken import AccessToken
    from dbmodels.event import Event
    from dbmodels.metrics import Metrics
    db.create_all()
    print('Created DB')

@app.cli.command("new_db")
def create_db():
    from dbmodels.accesstoken import AccessToken
    from dbmodels.event import Event
    from dbmodels.metrics import Metrics
    Event.__table__.drop(db.engine)
    AccessToken.__table__.drop(db.engine)
    Metrics.__table__.drop(db.engine)
    db.create_all()
    print('Created DB')

# Scheduler
# define the job
def scheduler_job():
    Scheduler.post_media()

scheduler = BackgroundScheduler()
# in your case you could change seconds to hours
scheduler.add_job(scheduler_job, trigger='interval', seconds=60)
scheduler.start()

# Shutdown your cron thread if the web process is stopped
atexit.register(lambda: scheduler.shutdown())

# Routes
@app.route('/')
def hello_world():
    from dbmodels.accesstoken import AccessToken
    user = AccessToken.query.filter(AccessToken.medium == 3).one()
    tBot = TwitterBot()
    hashtags = tBot.get_hashtags('#dream11ipl',user.token,user.token_2)
    return hashtags
    # return 'Hello, World!'

@app.route('/addEvent', methods=["POST"])
def addEvent():
    from dbmodels.accesstoken import AccessToken
    from dbmodels.event import Event
    data = request.json
    filename = ""
    if data['filename'] and data['file']:
            s3url = 'https://s3.us-east-2.amazonaws.com/'+os.getenv('S3BUCKET')+"/"
            filename = uuid.uuid4().hex+'.'+data['filename'].split('.')[1]
            S3Helper.upload_file(data['file'],os.getenv('S3BUCKET'),filename)
    for i in data['medium']:
        if i == "1":
            user = AccessToken.query.filter(AccessToken.name ==data['name']).filter(AccessToken.medium == i).one()
        else:
            user = AccessToken.query.filter(AccessToken.user_id ==data['user_id']).filter(AccessToken.medium == i).one()
        event = Event(
            social_id = user.social_id,
            medium = i,
            text = data['text'],
            notifications = True,
            filename= s3url+filename,
            sch_dt = datetime.strptime(data['sch_dt'], "%Y-%m-%dT%H:%M:%S.%fZ")
        )
        db.session.add(event)
        db.session.commit()
    return 'Hello, World!'

@app.route('/getEvents', methods=["POST"])
def getEvent():
    from dbmodels.event import Event
    from dbmodels.accesstoken import AccessToken 
    resp=[]
    data = request.json
    social_ids =[]
    for i in  AccessToken.query.with_entities(AccessToken.social_id).distinct():
        social_ids.append(i)
    print(social_ids)
    events = Event.query.filter(Event.medium.in_([1,2,3,4]))
    # .filter(Event.social_id.in_(social_ids)) # needs to be edit
    for s in events:
        events ={}
        events['id'] = s.id
        events['social_id'] = s.social_id
        events['medium'] = s.medium
        events['text'] = s.text
        events['req_dt'] = s.req_dt
        events['sch_dt']= s.sch_dt
        events['status']= s.status
        events['active']= s.active
        events['notification']= s.notifications
        events['filename']= s.filename
        events['remarks']= s.remarks
        resp.append(events)
    return jsonify(resp)

@app.route('/getStatus', methods=["POST"])
def getStatus():
    from dbmodels.accesstoken import AccessToken
    data = request.json
    resp=[]
    status = AccessToken.query.filter(AccessToken.user_id == data['user_id']).filter(AccessToken.exp_dt > datetime.now() ).filter(AccessToken.name != "")
    for s in status:
        medium ={}
        medium['medium'] = s.medium
        medium['name'] = s.name
        medium['social_id'] = s.social_id
        resp.append(medium)
    return jsonify(resp)

@app.route('/addToken', methods=["POST"])
def addToken():
    from dbmodels.accesstoken import AccessToken
    data = request.json
    if data['medium'] ==1:
        fbBot = FaceBookBot()
        newdata = fbBot.getToken(data['token'])
        # User Login Token
        user_token = AccessToken(
            social_id = data['social_id'],
            user_id = data['user_id'],
            medium = data['medium'],
            token = newdata['access_token'],
            exp_dt = datetime.utcnow()+timedelta(days= 18250)
            )
        # Page Token
        fbBot.getPageTokens(data['user_id'],data['social_id'],newdata['access_token'])
    else:
        user_token = AccessToken(
        social_id = data['social_id'],
        user_id = data['user_id'],
        medium = data['medium'],
        token = data['token'],
        exp_dt = datetime.utcnow()+timedelta(days= 18250)
        )
    db.session.add(user_token)
    db.session.commit()
    return 'Hello, World!'

# LinkedIn Callback Endpoint
@app.route('/getAuthUrl')
def get_AuthUrl():
    user_id = request.args.get("id")
    lBot = LinkedInBot()
    url = lBot.getAuthUrl()
    response = make_response(redirect(url))
    response.set_cookie('user_id', user_id)
    return response

# Instagram Login 
@app.route('/instagram_login')
def addInstagram():
    user_id = request.args.get('id')
    print(user_id)
    response = make_response(render_template('instagram_login.html'))
    response.set_cookie('user_id', user_id)
    return response

@app.route('/instagram_auth',methods=["POST"])
def check_Insta_auth():
    user_id = request.cookies.get('user_id')
    username = request.form.get("username")
    password = request.form.get("password")
    from media.instagram import InstagramBot
    insta_bot = InstagramBot()
    success = insta_bot.login(user_id,username,password)
    print(success)
    if success:
        return render_template('autoClose.html')
    else:
        return 'Login Failed'

# LinkedIn Callback Endpoint
@app.route('/callback')
def getAccessToken():
    user_id = request.cookies.get('user_id') #retrive the userid from the redirect Url
    code = request.args.get("code") #retrive access token
    lBot = LinkedInBot()    
    user_data = lBot.getAccessToken(user_id,code) #userId,firstname and lastname
    return render_template('autoClose.html')

@app.route('/t_getAuthUrl')
def get_AuthUrl_t():
    from dbmodels.accesstoken import AccessToken
    user_id = request.args.get("id")
    tBot = TwitterBot()
    url = tBot.getOAuthToken()
    response = make_response(redirect(url))
    response.set_cookie('user_id', user_id)
    return response

# Twitter Callback Endpoint
@app.route('/t_callback')
def getAccessToken_t():
    user_id = request.cookies.get('user_id')
    oauth_token = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')
    tBot = TwitterBot()
    url = tBot.getToken(user_id,oauth_token,oauth_verifier)
    return render_template('autoClose.html')

@app.route('/fb_stats/page_post_person_screens')
def getPagePostPersonScreens():
    from charts.facebook import PagePostPersonScreen,getAccesstoken
    access_token=getAccesstoken()
    df=PagePostPersonScreen(access_token)
    print(df)
    return "ok"

@app.route('/fb_stats')
def getPageMetrics():
    since = int(request.args.get("since"))
    until = int(request.args.get("until"))
    metrics = request.args.get('metrics')
    from charts.facebook import PageFansAge,getAccesstoken,getMetricsData,PageFansCity
    user_id = request.args.get('user_id')
    name = request.args.get('name')
    access_token=getAccesstoken(user_id,name)
    data={
        'page_fans': getMetricsData('page_fans',access_token,since,until),
        'page_views':getMetricsData('page_views_total',access_token,since,until),
        'page_likes':getMetricsData('page_actions_post_reactions_like_total',access_token,since,until),
        'page_age':PageFansAge(access_token),
        'page_city':PageFansCity(access_token)
    }
    return data

@app.route('/insta_stats')
def getInstagramData():
    user_id = request.args.get('user_id')
    name = request.args.get('name')
    from charts.instagram import insta_stats
    data = insta_stats(user_id,name)
    # print(data)
    return data

@app.route('/automation_settings',methods=["POST"])
def setInstagramAutomationSettings():
    from dbmodels.accesstoken import AccessToken
    from dbmodels.event import Event
    presets={"Fast":3,"Medium":6,"Slow":12}
    data = request.json
    print(data) 
    user_token = AccessToken(
            social_id = data['social_id'],
            user_id = data['user_id'],
            medium = 5,
            token = str(data),
            exp_dt = datetime.utcnow()+timedelta(days= 180)
            )
    db.session.add(user_token)
    interval = presets[data['automation_settings']["Activity Speed"]]
    print(interval)
    start_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    end = datetime.utcnow()+timedelta(days= 180)
    days =  data['automation_settings']["Days"]
    print(days)
    while start_time < end:
        if start_time.weekday() in days:
            for i in range(0,24,interval):
                event = Event(
                    social_id = data['social_id'],
                    medium = 5,
                    text = str(data),
                    notifications = True,
                    sch_dt = start_time + timedelta(hours= i)
                )
                db.session.add(event)
            db.session.commit()
        start_time += timedelta(days=1)
    return "success"