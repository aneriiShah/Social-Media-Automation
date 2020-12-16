import tweepy,sys,time
import requests
import os
from PIL import Image
from urllib.parse import quote,parse_qs
from datetime import datetime,timedelta
import random, string

from app import db
from dbmodels.accesstoken import AccessToken



class TwitterBot:
    consumer_key = 'eBcxNvQg2RIOi9QuY4LbyQtcu'
    consumer_secret = 'on05cmdiGyOduepEU7mUY2zCPDlRM7pbn9n30fZsrsdWgsfiJU'
    username="jaken4rmstatef1"


    def getOAuthToken(self):
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret,'http://localhost:5000/t_callback')
        redirect_url = auth.get_authorization_url()
        return redirect_url
    
    # https://developer.twitter.com/en/docs/authentication/api-reference/access_token
    def getToken(self,user_id,oauth_token,oauth_verifier):
        url = "https://api.twitter.com/oauth/access_token"
        body ={
            'oauth_consumer_key':self.consumer_key,
            'oauth_token':oauth_token,
            'oauth_verifier':oauth_verifier
        }
        response = requests.post(url, data=body)
        response = response.text
        a = parse_qs(response)
        # Fetching User Handle
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(a['oauth_token'][0], a['oauth_token_secret'][0])
        api =tweepy.API(auth)
        user = api.get_user(a['user_id'][0])
        user_token = AccessToken(
            social_id = a['user_id'][0],
            user_id =user_id,
            name=user.screen_name,
            medium =3,
            token = a['oauth_token'][0],
            token_2 =a['oauth_token_secret'][0],
            exp_dt = datetime.utcnow() + timedelta(days= 18250)
            )
        db.session.add(user_token)
        db.session.commit()
        return a

    def image_post(self,text,image_url,access_token,access_token_secret):
        f = open('./images/newimage_t.jpg','wb')
        f.write(requests.get(image_url).content)
        f.close()
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api =tweepy.API(auth)
        api.update_with_media('./images/newimage_t.jpg', text )

    def clean_input(self,tag):
        tag =tag.replace(" ","")
        if tag.startswith('#'):
            return tag[1:].lower()
        else:
            return tag.lower()  
    
    def return_all_hashtags(self,tweets, tag):
        all_hashtags=[]
        for tweet in tweets:
            for word in tweet.split():
                if word.startswith('#') and word.lower() != '#'+tag.lower():
                    all_hashtags.append(word.lower())
        return all_hashtags
    
    def get_hashtags(self,tag,access_token,access_token_secret):
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api =tweepy.API(auth)
        search_tag=self.clean_input(tag)
        tweets = tweepy.Cursor(api.search,
                q='#'+search_tag,
                lang="en").items(200)
        tweets_list=[] 
        for tweet in tweets:
            tweets_list.append(tweet.text)
        all_tags= self.return_all_hashtags(tweets_list, search_tag)
        frequency={} 
        for item in set(all_tags):
            frequency[item]=all_tags.count(item)
        return {k: v for k, v in sorted(frequency.items(), 
                    key=lambda item: item[1], reverse= True)}

    
    

    def get_potentialfollowers(username): 
          
        # Authorization to consumer key and consumer secret 
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 
  
        # Access to user's access key and access secret 
        auth.set_access_token(access_key, access_secret) 
  
        # Calling api 
        api = tweepy.API(auth)
        followers =api.followers(username)
        tweetsnew_for_screenname =[follower.screen_name for follower in followers]
        print(tweetsnew_for_screenname)
        tweets = api.user_timeline(screen_name=username) 
        tweetsnew_for_id =[tweet.id for tweet in tweets] 
        retweeters_screenname=[]
        main_list=[]
        # Retweets on our posts and who retweeted it 
        for id in tweetsnew_for_id:
             retweets_list = api.retweets(id)
             for retweet in retweets_list:
                retweeters_screenname.append(retweet.user.screen_name)
                
        print(retweeters_screenname) 
          
        main_list = setdiff_ans(retweeters_screenname,tweetsnew_for_screenname)
        print(main_list)
             
        


def setdiff_ans(array1,array2):
    ans = np.setdiff1d(array1,array2).tolist()
    return ans
