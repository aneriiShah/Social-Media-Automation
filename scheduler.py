from datetime import datetime,timedelta
from app import db

from dbmodels.accesstoken import AccessToken
from dbmodels.event import Event
from media.linkedIn import LinkedInBot
from media.twitter import TwitterBot
from media.facebook import FaceBookBot




class Scheduler:
    @staticmethod
    def post_media():
        start_time = datetime.utcnow().replace(microsecond=0)
        end_time = start_time + timedelta(seconds= 59,microseconds=999999)
        print(start_time,end_time)
        events = Event.query.filter( Event.sch_dt >=  start_time ).filter(Event.sch_dt < end_time ).filter( Event.active == True)
        for event in events:
            user = AccessToken.query.filter(AccessToken.social_id == event.social_id).filter(AccessToken.medium == event.medium).one()
            if event.medium == "1":
                if event.filename:
                    fb_Bot = FaceBookBot()
                    resp = fb_Bot.postPhotos(user.social_id,event.filename,event.text,user.token)
                    try:
                        event.remarks = resp.post_id
                        event.active = False
                    except:
                        event.status = 'error'
            # elif event.medium == "2":
            elif event.medium == "3":
                t_Bot = TwitterBot()
                t_Bot.image_post(event.text,event.filename,user.token,user.token_2)
                event.active = False
                db.session.commit()
            elif event.medium == "4":
                    # if not event.filename:
                        # LinkedInBot.getAuthUrl()
                lBot = LinkedInBot()
                a = lBot.image_post(user.social_id,user.token,event.text,'','',event.filename)
                event.active = False
                db.session.commit()                         
           
