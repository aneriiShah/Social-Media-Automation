import requests
import os
from datetime import datetime,timedelta
from flask import redirect,request
from app import db
from dbmodels.accesstoken import AccessToken
from urllib.parse import quote


class FaceBookBot:
    app_id = os.getenv('FACEBOOK_APP_ID')
    secret = os.getenv('FACEBOOK_CLIENT_SECRET')
    fb_url = "https://graph.facebook.com"

    # Function to change Short-lived access tokens for Long-lived Page access tokens
    def getToken(self,accessToken):
        url = self.fb_url+"/oauth/access_token?grant_type=fb_exchange_token&client_id="+self.app_id+"&client_secret="+self.secret+"&fb_exchange_token="+accessToken
        resp = requests.get(url).json()
        print(resp)
        return resp 

    #https://developers.facebook.com/docs/pages/access-tokens#get-access-tokens-of-pages-you-manage 
    def getPageTokens(self,user_id,social_id,access_token):
        url = self.fb_url+"/"+social_id+"/accounts?access_token="+access_token
        resp = requests.get(url)
        resp = resp.json()
        print(resp)
        for data in resp['data']:
            token = self.getToken(data['access_token'])
            user_token = AccessToken(
            social_id = data['id'],
            user_id = user_id,
            medium = 1,
            token = token['access_token'],
            name = data['name'],
            exp_dt = datetime.utcnow()+ timedelta(days= 18250)
            )
            db.session.add(user_token)
        db.session.commit()
        return resp

    def postPhotos(self,social_id,photo,message,accessToken):
        url = self.fb_url+"/"+social_id+"/photos?url="+photo+"&access_token="+accessToken+"&message="+quote(message)
        resp = requests.post(url)
        try:
            resp = resp.json()
            print('Message Posted')
            return resp
        except:
            return False

    def postMessage():
        print("postMessage")
        