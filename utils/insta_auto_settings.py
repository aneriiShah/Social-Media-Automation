import sys, json, time, random
from .InstagramAPI import InstagramAPI as InstaAPI
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from instabot import Bot
import requests_toolbelt
import pandas as pd
import requests
import csv
import datetime
import os


from time import sleep, strftime
from random import randint

class instaAutoSettings():
    def __init__(self,username,password):
        # self.data=data
        self.username=username
        self.password=password
        self.followers = []
        self.followings = []
        self.api = api  = InstaAPI(username, password)

    def info(self):
        print("I follow them but they dont follow me:\n")
        tot = 0
        for i in self.followings:
            if i not in self.followers:
                tot=tot+1
                print(str(tot)+" "+i)		
        print("\nTotal: "+str(tot))

        print("\nThey follow me but i dont follow them:\n")
        tot = 0
        for i in self.followers:
            if i not in self.followings:
                tot=tot+1
                print(str(tot)+" "+i)	
        print("\nTotal: "+str(tot))
    
    def get_id(self,username):
        url = "https://www.instagram.com/web/search/topsearch/?context=blended&query="+username+"&rank_token=0.3953592318270893&count=1"
        response = requests.get(url)
        respJSON = response.json()
        try:
            users = str( respJSON['users'])
            user_id = ''
            for i in range(len(users)):
                user_name = str( respJSON['users'][i].get("user").get("username") )
                if user_name == username:
                    user_id = str( respJSON['users'][i].get("user").get("pk") )
                    return user_id
        except:
            print(respJSON)
            return "Unexpected error"

    def get_profile_pic_url(self,username):
        url = "https://www.instagram.com/web/search/topsearch/?context=blended&query="+username+"&rank_token=0.3953592318270893&count=1"
        response = requests.get(url)
        respJSON = response.json()
        try:
            users = str( respJSON['users'])
            profile_pic_url = ''
            for i in range(len(users)):
                user_name = str( respJSON['users'][i].get("user").get("username") )
                if user_name == username:
                    profile_pic_url = str( respJSON['users'][i].get("user").get("profile_pic_url") )
                    return profile_pic_url
        except:
            print(respJSON)
            return "Unexpected error"
        
    def getTotalSelfFollowers(self):
        for i in api.getTotalSelfFollowers():
            self.followers.append(i.get("username"))
            
    def getTotalSelfFollowings(self):	
        for i in api.getTotalSelfFollowings():
            followings.append(i.get("username"))
            
    def profile_pic_url_list(self):
        profile_pic_urls_list = []
        for i in self.followers:
            profile_pic_url = self.get_profile_pic_url(i)
            profile_pic_urls_list.append(profile_pic_url)
            print("UserName= "+i+" Profile pic url = "+profile_pic_url)
            return profile_pic_urls_list
       
    def selenium_starter(self):
        chromedriver_path = 'C:/Users/aneri/Downloads/chromedriver_win32/chromedriver.exe' # Change this to your own chromedriver path!
        webdriv = webdriver.Chrome(executable_path=chromedriver_path)
        sleep(2)
        webdriv.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
        sleep(3)

        username = webdriv.find_element_by_name('username')
        username.send_keys(self.username)
        password = webdriv.find_element_by_name('password')
        password.send_keys(self.password)

        button_login = webdriv.find_element_by_css_selector('#loginForm > div > div:nth-child(3) > button')
        button_login.click()
        sleep(3)

        notnow = webdriv.find_element_by_css_selector('#react-root > section > main > div > div > div > div > button')
        notnow.click() #comment these last 2 lines out, if you don't get a pop up asking about notifications

        notnow2 = webdriv.find_element_by_css_selector('body > div.RnEpo.Yx5HN > div > div > div > div.mt3GC > button.aOOlW.HoLwm')
        notnow2.click()
        return webdriv
    
    def like_posts(self,target):
        webdriv=self.selenium_starter()
        tag = -1	
        likes = 0
        comments = 0

        for hashtag in target:
            tag += 1
            webdriv.get('https://www.instagram.com/explore/tags/'+ target[tag] + '/')
            sleep(5)
            first_thumbnail = webdriv.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div')
            first_thumbnail.click()
            sleep(randint(1,2))    
            try:        
                for x in range(1,MAXIMO):
                    # Liking the picture
                    button_like = webdriv.find_element_by_xpath('/html/body/div[5]/div[2]/div/article/div[3]/section[1]/span[1]/button')      
                    button_like.click()
                    likes += 1
                    sleep(randint(18,25))

                    # Next picture
                    link = webdriv.find_element_by_link_text('Next')
                    link.click()
                    sleep(randint(25,29))
            except:
                continue
        
    def comment_posts(self,target,preset_comments):
        webdriv=self.selenium_starter()
        tag = -1	
        likes = 0
        comments = 0

        for hashtag in target:
            tag += 1
            webdriv.get('https://www.instagram.com/explore/tags/'+ target[tag] + '/')
            sleep(5)
            first_thumbnail = webdriv.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div')
            first_thumbnail.click()
            sleep(randint(1,2))    
            try:        
                for x in range(1,MAXIMO):
                    # Comments and tracker
                    comm_prob = randint(1,10)
                    print('{}_{}: {}'.format(hashtag, x,comm_prob))
                    if comm_prob > 5:
                        comments += 1
                        webdriv.find_element_by_xpath('/html/body/div[5]/div[2]/div/article/div[3]/section[1]/span[2]/button/div/svg').click()
                        comment_box = webdriv.find_element_by_xpath('/html/body/div[5]/div[2]/div/article/div[3]/section[3]/div/form/textarea')
                        if (comm_prob < 7):
                            comment_box.send_keys(preset_comments[0])
                            sleep(1)
                        elif (comm_prob > 6) and (comm_prob < 9):
                            comment_box.send_keys(preset_comments[1])
                            sleep(1)
                        elif comm_prob <= 9:
                            comment_box.send_keys(preset_comments[2])
                            sleep(1)
                        # Enter to post comment
                        comment_box.send_keys(Keys.ENTER)
                        sleep(randint(22,28))

                    # Next picture
                    link = webdriv.find_element_by_link_text('Next')
                    link.click()
                    sleep(randint(25,29))
            except:
                continue
        
    def hashtag_recommendation(self,target):
        for each in target:
            url = 'https://www.instagram.com/web/search/topsearch/?context=blended&query=%23' + hashtag + '&include_reel=true'
            resp = requests.get(url).json()
            hash_list = resp["hashtags"]
            hashtag_list = []
            for each in hash_list:
                new_dict = {'name': each["hashtag"]["name"], 'media_count': each["hashtag"]["media_count"], 'media_count_roundoff': each["hashtag"]["search_result_subtitle"]}
                hashtag_list.append(new_dict)
                print(new_dict)
    
    def follow_tag(self,target):
        for tag in target:
            api.tagFeed(tag)
            media_id = api.LastJson 
            tot = 0
            new_followers = []
            old_followers = []
            old_users = []
            fname = "followers.csv"
            
            old_followers = pd.read_csv(fname)
            old_users = old_followers["UserId"]
            old_users = set(old_users)
                
            print("\nTAG: "+str(tag)+"\n")
            for i in media_id["items"]:
                time.sleep(float( random.uniform(min_delay*10,max_delay*10) / 10 ))
                username = i.get("user")["username"]
                user_id = i.get("user")["pk"]
                current_time = datetime.datetime.now() 
                timestamp = current_time.timestamp()
                if int(user_id) in old_users:
                    print("old_User")
                else:
                    api.follow(user_id)
                    new_followers.append([user_id,username,timestamp])
                    tot += 1
                    print("Following "+str(username)+" (with id "+str(user_id)+")")	
                    if(tot>=MAXIMO):
                        break
            with open(fname,"a",encoding="utf-8",newline="") as csv_file:
                writer = csv.writer(csv_file)
                #writer.writerow(("UserId","UserName","Timestamp"))
                for each in new_followers:
                    writer.writerow((each[0],each[1],each[2]))		
            print("Total: "+str(tot)+" for tag "+tag+" (Max val: "+str(MAXIMO)+")\n")
            
    def printUsage(self):
        print("Usage: \n+ python main.py -u USERNAME -p PASSWORD -o info: Show report")
        print("+ python main.py -u USERNAME -p PASSWORD -o follow-tag -t TAG: Follow users using the tags you introduce")
        print("+ python main.py -u USERNAME -p PASSWORD -o follow-location -t LOCATION_ID: Follow users from a location")
        print("+ python main.py -u USERNAME -p PASSWORD -o super-followback: Follow back all the users who you dont follow back")
        print("+ python main.py -u USERNAME -p PASSWORD -o super-unfollow: Unfollow all the users who dont follow you back")
        print("+ python main.py -u USERNAME -p PASSWORD -o unfollow-all: Unfollow all the users")
    
    def follow_location(self,target):
        for each in target:
            if each is not None:
                api.getLocationFeed(target)
                media_id = api.LastJson
                tot = 0
                new_followers = []
                old_followers = []
                old_users = []
                fname = "followers.csv"
                
                old_followers = pd.read_csv(fname)
                old_users = old_followers["UserId"]
                old_users = set(old_users)
                for i in media_id.get("users"):
                    user_id = ''
                    time.sleep(float( random.uniform(min_delay*10,max_delay*10) / 10 ))
                    username = i.get("username")
                    user_id = self.get_id(username)
                    current_time = datetime.datetime.now() 
                    timestamp = current_time.timestamp()
                    if int(user_id) in old_users:
                        print("Old user")
                    else:
                        api.follow(user_id)
                        new_followers.append([user_id,username,timestamp])
                        tot += 1
                        print("Following "+str(username)+" (with id "+str(user_id)+")")	
                        if(tot>=MAXIMO):
                            break
                        
                with open(fname,"a",encoding="utf-8",newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    #writer.writerow(("UserId","UserName","Timestamp"))
                    for each in new_followers:
                        writer.writerow((each[0],each[1],each[2]))		
                print("Total: "+str(tot)+" for tag "+target+" (Max val: "+str(MAXIMO)+")\n")
                
    def super_followback(self):
        count = 0
        for i in self.followers:
            if i not in followings:
                count+=1
                time.sleep(float( random.uniform(min_delay*10,max_delay*10) / 10 ))
                user_id = self.get_id(i)
                print(str(count)+") Following back "+i)
                api.follow(user_id)
    
    def super_unfollow(self):
        whitelist = open("whitelist.txt").read().splitlines()
        count = 0
        old_followers = pd.read_csv("followers.csv")
        for i in self.followings:
            if (i not in self.followers) and (i not in whitelist):
                count+=1
                time.sleep(float( random.uniform(min_delay*10,max_delay*10) / 10 ))
                user_id = self.get_id(i)
                print(str(count)+") Unfollowing "+i)
                api.unfollow(user_id)
                old_followers = old_followers[old_followers.UserId != int(user_id)]
                old_followers.to_csv("followers.csv",index="False",encoding='utf-8',index_label=False)
    
    def unfollowall(self):
        count = 0
        old_followers = pd.read_csv("followers.csv")
        for i in self.followings:
            count +=1
            time.sleep(float( random.uniform(min_delay*10,max_delay*10) / 10 ))
            user_id = self.get_id(i)
            print(str(count)+") Unfollowing "+i)
            api.unfollow(user_id)
            old_followers = old_followers[old_followers.UserId != int(user_id)]
            old_followers.to_csv("followers.csv",index="False",encoding='utf-8',index_label=False)
            
    def bot(self):
        self.info()
        self.getTotalSelfFollowers()
        self.profile_pic_url_list()
        self.like_posts(target)
        self.comment_posts(target,preset_comments)
        self.hashtag_recommendation(target)
        self.follow_tag(target)
        self.printUsage()
        self.follow_location(target)
        self.super_followback()
        self.super_unfollow()
        self.unfollowall()