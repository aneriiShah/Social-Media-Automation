import time
import pandas as pd
from InstagramAPI import InstagramAPI
from pandas.io.json import json_normalize
from dbmodels.accesstoken import AccessToken

def login_to_instagram(username, password):
    api = InstagramAPI(username, password)
    api.login()
    return api

def get_my_posts(api):
    '''Retrieve all posts from own profile'''
    my_posts = []
    has_more_posts = True
    max_id= ''

    while has_more_posts:
        api.getSelfUserFeed(maxid=max_id)
        if api.LastJson['more_available'] is not True:
            has_more_posts = False #stop condition

        max_id = api.LastJson.get('next_max_id','')
        my_posts.extend(api.LastJson['items']) #merge lists
        time.sleep(2) # slows down to avoid flooding

        if has_more_posts:
            print(str(len(my_posts)) + ' posts retrieved so far...')

    print('Total posts retrieved: ' + str(len(my_posts)))
    
    return my_posts

def get_posts_likers(api, my_posts):
    '''Retrieve all likers on all posts'''
    
    likers = []
    
    print('wait %.1f minutes' % (len(my_posts)*2/60.))
    for i in range(len(my_posts)):
        m_id = my_posts[i]['id']
        api.getMediaLikers(m_id)
        
        likers += [api.LastJson]
        
        # Include post_id in likers dict list
        likers[i]['post_id'] = m_id
        
        time.sleep(2)
    print('done')
    
    return likers

def get_posts_commenters(api, my_posts):
    '''Retrieve all commenters on all posts '''
    
    commenters = []
    
    print('wait %.1f minutes' % (len(my_posts)*2/60.))
    for i in range(len(my_posts)):
        m_id = my_posts[i]['id']
        api.getMediaComments(m_id)
        
        commenters += [api.LastJson]
        
        # Include post_id in commenters dict list
        commenters[i]['post_id'] = m_id
            
        time.sleep(2)
    print('done')
    
    return commenters

def posts_likers_to_df(likers):
    '''Transforms likers list of dicts into pandas DataFrame'''
    
    # Normalize likers by getting the 'users' list and the post_id of each like
    df_likers = json_normalize(likers, 'users', ['post_id'])
    
    # Add 'content_type' column to know the rows are likes
    df_likers['content_type'] = 'like'
    
    df_likers = df_likers.groupby(['username','profile_pic_url']).size().reset_index(name='counts').sort_values(by='counts',ascending=False)
    max = df_likers['counts'].max()
    min = df_likers['counts'].min()

    return {'data':df_likers.to_dict(orient='records'),'max':int(max),'min':int(min)}

def posts_commenters_to_df(commenters):
    '''Transforms commenters list of dicts into pandas DataFrame'''
    
    # Include username and full_name of commenter in 'comments' list of dicts
    for i in range(len(commenters)):
        if len(commenters[i]['comments']) > 0: # checks if there is any comment on the post
            for j in range(len(commenters[i]['comments'])):
                # Puts username/full_name one level up
                commenters[i]['comments'][j]['username'] = commenters[i]['comments'][j]['user']['username']
                commenters[i]['comments'][j]['full_name'] = commenters[i]['comments'][j]['user']['full_name']
                
    # Create DataFrame
    # Normalize commenters to have 1 row per comment, and gets 'post_id' from parent 
    df_commenters = json_normalize(commenters, 'comments', 'post_id')
    
    # DateTime conversion
    df_commenters.created_at = pd.to_datetime(df_commenters.created_at, unit='s')
    df_commenters.created_at_utc = pd.to_datetime(df_commenters.created_at_utc, unit='s')
    df_commenters['created_at_ch'] = df_commenters.created_at_utc.dt.tz_localize('UTC').dt.tz_convert('America/Chicago')
    days = df_commenters.created_at_ch.dt.weekday.value_counts().sort_index()
    # Get rid of 'user' column as we already handled it above
    #del df_commenters['user']
    df_commenters = df_commenters.groupby(['username','user.profile_pic_url']).size().reset_index(name='counts').sort_values(by='counts',ascending=False)
    max = df_commenters['counts'].max()
    min = df_commenters['counts'].min()

    return {'users':{'data':df_commenters.to_dict(orient='records'),'max':int(max),'min':int(min)},
            'days':{'data':days.to_dict(),'max':1,'min':1}}

def insta_stats(user_id,name):
    user = AccessToken.query.filter(AccessToken.name == name).filter(AccessToken.user_id == user_id).one()
    api=login_to_instagram(user.name, user.token)
    my_posts = get_my_posts(api)
    commenters = get_posts_commenters(api, my_posts)
    likers = get_posts_likers(api, my_posts)
    df_likers = posts_likers_to_df(likers)
    df_commenters = posts_commenters_to_df(commenters)
    return {'comments':df_commenters,
            'likes':df_likers }