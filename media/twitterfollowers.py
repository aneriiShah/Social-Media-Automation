import tweepy #https://github.com/tweepy/tweepy
import csv
import matplotlib.pyplot as plot
import pandas as pd
import numpy as np



#Twitter API credentials
consumer_key = 'eBcxNvQg2RIOi9QuY4LbyQtcu' 
consumer_secret = 'on05cmdiGyOduepEU7mUY2zCPDlRM7pbn9n30fZsrsdWgsfiJU'
access_key = '1307741523065352193-Lib8JoXvX0C7EWyMin00exqfMZJuN3'
access_secret = 'jGmgNCF3FwcThuBKhruxevbLD5jD73v57yyJ9I24XRs8B'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

name ="jaken4rmstatef1"




count = 0


# Function to extract tweets 
def get_tweets(username): 
          
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

        
# Driver code 
if __name__ == '__main__': 
  
    # Here goes the twitter handle for the user 
    # whose tweets are to be extracted. 
    get_tweets("jaken4rmstatef1")  