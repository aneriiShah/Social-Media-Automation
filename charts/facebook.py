import requests
import pandas as pd
import json, operator
from datetime import datetime,timedelta
from app import db
from dbmodels.accesstoken import AccessToken
from dbmodels.metrics import Metrics



def interValDays(since,until):
    seconds_day = 24*60*60
    days = (until - since) / seconds_day
    intervals=[]
    if days < 90:
        since = until - 90* seconds_day # default API call interval to 90 days
        intervals.append([since,until])
    else: #Split user requested interval to 90days interval
        while since < until:
            intervals.append([since ,since + 90* seconds_day])
            since+= 90* seconds_day
    return intervals

def getAccesstoken(user_id,name):
    user = AccessToken.query.filter(AccessToken.name == name).filter(AccessToken.user_id == user_id).one()
    return user

def PageFansCity(access_token):
        resp = requests.get('https://graph.facebook.com/v8.0/'+access_token.social_id+'/insights?access_token='+access_token.token+'&metric=page_fans_city,page_fans')
        resp= resp.json()
        arr=[]
        count = resp['data'][0]['values'][1]['value']
        for (k, v) in count.items():
            r=[]
            city_data = k.split(',')
            city_data.reverse()
            if len(city_data) == 2:
                city_data.insert(1, 'NA')
            if len(city_data) == 1:
                city_data.insert(0, 'NA')
                city_data.insert(0, 'NA')
            for i in range(0,3):
                r.append(city_data[i])
            r.append(v)
            arr.append(r)
        df = pd.DataFrame(arr,columns=['Country','PR','City','Count'])
        df['percent'] = (df['Count'] /  resp['data'][1]['values'][1]['value']) * 100
        # print(df)
        return df.to_dict(orient='records')

def PageFansAge(access_token):
    url = 'https://graph.facebook.com/v8.0/'+access_token.social_id+'/insights?access_token='+access_token.token+'&metric=page_fans_gender_age,page_fans'
    resp = requests.get(url)
    resp = resp.json()
    data= resp['data'][0]['values'][1]['value']
    arr={}
    for (k, v) in data.items():
        r =[]
        for a in k.split('.'):
            r.append(a)
        try:
            d = arr[r[1]]
            d[r[0]]=v
        except:
            arr[r[1]]={r[0]:v}
    result = []
    for (k, v) in arr.items():
        a ={'name':k}
        a.update(v)
        result.append(a)
    result.sort(key=operator.itemgetter('name'))
    return {'data':result,'total':resp['data'][1]['values'][1]['value']}

def PagePostPersonScreen(access_token):
    resp = requests.get('https://graph.facebook.com/v8.0/'+access_token.social_id+'/insights?access_token='+access_token+'&metric=page_posts_impressions')
    resp= resp.json()
    data= resp['data']
    arr={}
    d=[]
    for k in data:
        period=k.get('period')
        values=k.get('values')[0]['value']
        arr[period]=values
    for k in arr:
        t={}
        t["name"]=k
        t["value"]=arr[k]
        d.append(t)
    print(d)
    return json.dumps(d)

def getMetricsData(metrics,access_token,since,until):
    d=[]
    start_query = datetime.fromtimestamp(since)
    end_query = datetime.fromtimestamp(until)
    seconds_day = 24*60*60
    data = Metrics.query.filter( Metrics.datetime >=  start_query ).filter(Metrics.datetime < end_query ).filter( Metrics.metrics == metrics).filter( Metrics.social_id == access_token.social_id)
    print(data.count())
    if data.count() != (int((until - since)/seconds_day)):
    # if 0 == 1:
        intervals = interValDays(since,until)
        for i in intervals:
            resp = requests.get('https://graph.facebook.com/v8.0/'+access_token.social_id+'/insights?access_token='+access_token.token+'&metric='+metrics+'&since='+str(i[0])+'&until='+str(i[1]))
            resp= resp.json()
            data= resp['data']
            arr={}
            d=[]
            for k in data:
                period=k.get('period')
                if period == "day":
                    for m in k.get('values'):
                        date_time_obj = datetime.strptime(m['end_time'], '%Y-%m-%dT%H:%M:%S%z')
                        metric_data_day = Metrics(
                            social_id = access_token.social_id,
                            medium = access_token.medium,
                            datetime = date_time_obj,
                            metrics = metrics,
                            value= m['value']
                        )
                        db.session.add(metric_data_day)
                        try:
                            db.session.commit()
                        except:
                            db.session.rollback()
    data = Metrics.query.filter( Metrics.datetime >=  start_query ).filter(Metrics.datetime < end_query ).filter( Metrics.metrics == metrics).filter( Metrics.social_id == access_token.social_id).order_by(Metrics.datetime.asc())
    for i in data:
        t={}
        t["name"] = i.datetime.timestamp()
        t["value"] = i.value
        d.append(t)
    return d

def PageViews(access_token,since,until):
    return  getMetricsData('page_views_total',access_token,since,until)

def PageLikes(access_token,since,until):
    return getMetricsData('page_actions_post_reactions_like_total',access_token,since,until)