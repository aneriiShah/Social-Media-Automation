import requests
import os
from flask import redirect,request
from app import db
from datetime import datetime,timedelta
from dbmodels.accesstoken import AccessToken


class LinkedInBot:
    #base api url
    api_url_base = 'https://api.linkedin.com/v2/'
    #Values fetched from environment files
    #redirect url set in linkedIn developer account
    redirect_uri = os.getenv('LINKEDIN_REDIRECT_URI')
    #app_id,app_secret of developer account
    app_id = os.getenv('LINKEDIN_APP_ID')
    app_secret = os.getenv('LINKEDIN_APP_SECRET')
    #Scope and state of linkedIn developer accound
    scope = os.getenv('LINKEDIN_SCOPE')
    state = os.getenv('LINKEDIN_STATE') 

    #function returns the standard header
    def getHeader(self,access_token):
        headers = {'X-Restli-Protocol-Version': '2.0.0',
               'Content-Type': 'application/json',
               'Authorization': f'Bearer {access_token}'}
        return headers

    #Simple post share
    def simple_post(self,person_id,access_token,visibility,post_text):
        api_url = f'{self.api_url_base}ugcPosts'
        post_data = {
            "author": f"urn:li:person:{person_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": post_text #post content
                    },
                    "shareMediaCategory": "NONE"
                },
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility #visibility of the post
            },
        }
        headers = self.getHeader(access_token) 
        response = requests.post(api_url, headers=headers, json=post_data)
        if response.status_code == 201:
            print("Post Successfully posted")
        else:
            print("Post Unsuccessfull")
            print(response.content)

    #article share
    def article_post(self,person_id,access_token,visibility,post_text,link_title,link_desc,link_url):
        api_url = f'{self.api_url_base}ugcPosts'
        post_data = {
            "author": f"urn:li:person:{person_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": post_text #article content
                    },
                    "shareMediaCategory": "ARTICLE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": link_desc #post content
                            },
                            "originalUrl": link_url, #url for article
                            "title": {
                                "text": link_title #article title
                            }
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility #visibility of the post
            }
        }
        headers = self.getHeader(access_token) 
        response = requests.post(api_url, headers=headers, json=post_data)

        if response.status_code == 201:
            print("Article posted successfully")
            print(response.content)
        else:
            print("Post unsuccessfull")
            print(response.content)

    #register to upload image
    def registerUploadRequest(self,person_id,access_token,file):
        api_url = f'{self.api_url_base}assets?action=registerUpload'
        registerUploadRequest = {
            "registerUploadRequest": {
                "recipes": [
                    "urn:li:digitalmediaRecipe:feedshare-image"
                ],
                "owner": f"urn:li:person:{person_id}",
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        headers = self.getHeader(access_token) 
        response = requests.post(api_url, headers=headers,json=registerUploadRequest)
        if response.status_code == 200:
            print("registerUploadRequest succeed")
            res = response.json()
            # Upload your image to LinkedIn
            uploadUrl = res['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            self.uploadImage(uploadUrl,file,access_token)
            return res
        else:
            print("RegisterUploadRequest failed")
            return ""
        
    #image share need to upload image before posting
    def uploadImage(self,uploadUrl,file,access_token):
        files = open(file ,"rb").read()
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.put(uploadUrl, data=files, headers=headers)
        if response.status_code == 201:
            print("Image Uploaded")
        else:
            print("Image upload failed")
            
    #Image share 
    def image_post(self,person_id,access_token,post_text,image_title,image_desc,image_url):
        filename = './images/newimage.jpg'
        f = open('./images/newimage.jpg','wb')
        f.write(requests.get(image_url).content)
        f.close()
        api_url = f'{self.api_url_base}ugcPosts'
        register_resp=self.registerUploadRequest(person_id,access_token,filename)
        if(register_resp!=""):
            post_data = {
                "author": f"urn:li:person:{person_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                        "text": post_text                #post content    
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": [
                            {
                                "status": "READY",
                                "description": {
                                    "text": image_desc #Description of image 
                                },
                                "media": register_resp['value']['asset'],
                                "title": {
                                    "text": image_title #Image title 
                                }
                            }
                        ]
                    },
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "CONNECTIONS"
                },
            }
            headers = self.getHeader(access_token) 
            response = requests.post(api_url, headers=headers, json=post_data)

            if response.status_code == 201:
                print("Posted Successfully")
        else:
            print("Post unsuccessful")

    #return the redirecting url upon signin
    def getAuthUrl(self):
        url = "https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=" + self.app_id + "&redirect_uri="+ self.redirect_uri + "&scope=" + self.scope + "&state" + self.state
        return url

    #function to retrive access token
    def getAccessToken(self,user_id,code):
        url = "https://www.linkedin.com/oauth/v2/accessToken?"
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        params={"client_id":self.app_id,"client_secret":self.app_secret,"grant_type":"authorization_code","redirect_uri":self.redirect_uri,"code":code}
        response = requests.post(url, params=params, headers=headers)
        if response.status_code == 200:
            res = response.json()
            access_token = res['access_token']
            person_details = self.getPersonDetails(access_token)
            user_token = AccessToken(
                social_id = person_details[0],
                name = person_details[1],
                user_id = user_id,
                medium = 4,
                token = access_token,
                exp_dt = datetime.utcnow()+timedelta(days=18250)
            )
            db.session.add(user_token)
            db.session.commit()
            return [person_details[0],access_token]
        else:
            return "Authentication failed.Relogin"
        # return redirect(url)

    #function to retrive user personId,firstname and lastname
    @staticmethod      
    def getPersonDetails(access_token):
        url = "https://api.linkedin.com/v2/me"
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        params={"oauth2_access_token":access_token}
        response = requests.get(url, params=params, headers=headers)
        print (response.status_code)
        if response.status_code == 200:
            res = response.json()
            personID = res['id']
            firstName = res['localizedFirstName']
            lastName = res.get('localizedLastName',None)
            return [personID,firstName,lastName]
        else:
            return "Fetching userdetails failed"
        # return redirect(url)