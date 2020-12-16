from instabot import Bot
from datetime import datetime,timedelta
import os
import schedule
import time
from app import db
from dbmodels.accesstoken import AccessToken

# pic = "\\images\\social-media-best-size-8-copy-2.jpg"
# caption = "My first post"

class InstagramBot:
    bot = Bot()
    def post(self,username,password):
        self.bot.login(username=username, password=password)
        self.bot.logger.info("Uploading pic `{pic}` with caption: `{caption}`".format(pic=pic,caption=caption))
        if not bot.upload_photo(pic, caption=caption):
            bot.logger.error("Something went wrong...")
            #break

    def login(self,user_id,username,password):
        try:            
            self.bot.login(username=username, password=password,is_threaded=True)
            social_id = self.bot.get_user_id_from_username(username)
            user_token = AccessToken(
            social_id = social_id,
            user_id = user_id,
            medium = 2,
            token = password,
            name = username,
            exp_dt = datetime.utcnow()+ timedelta(days= 18250)
            )
            db.session.add(user_token)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            return False