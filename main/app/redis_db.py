import redis
import json
import yaml

api_db = redis.Redis('127.0.0.1','6379',db=0)


def insert_value(name,method,endpoint,maintainer,payload,output):
    try:
        api_id = int(max(api_db.keys())) + 1
    except:
        api_id = 1
    api_db.hmset(api_id,{'id':api_id,'name' : name,'method' : method,'endpoint' : endpoint,'maintainer' : maintainer,'payload' : payload, 'output' : output, 'status' : 'not available', 'result' : 'not available','efficiency':'not available'})


def get_data(user_id):
    return api_db.hgetall(user_id)
    
def get_value():
    db = []
    api_id = api_db.keys()
    api_id.sort()
    for api in api_id:
        temp = api_db.hgetall(api)
        db.append(temp)
    return db



def get_keys():
    api_id = api_db.keys()
    return api_id



def get_keys_value():
    api_id = api_db.keys()
    api_id.sort()
    values = []
    for api in api_id:
        if(api_db.hget(api,'efficiency') == 'not available'):
            values.append('0')
        else:
            values.append(api_db.hget(api,'efficiency'))
    return api_id,values
    

def update_value(api_id,api_name,method,endpoint,maintainer,payload,output,checkbox):
    if(checkbox):
        api_db.delete(api_id)
    else:
        if(api_name != ''):
            api_db.hmset(api_id,{'name':api_name})
        if(method != ''):
            api_db.hmset(api_id,{'method':method})
        if(endpoint != ''):
            api_db.hmset(api_id,{'endpoint':endpoint})
        if(maintainer != ''):
            api_db.hmset(api_id,{'maintainer':maintainer})
        if(payload != ''):
            api_db.hmset(api_id,{'payload':payload})
        if(output != ''):
            api_db.hmset(api_id,{'output':output})

def change_value(api_id,param,value):
    if(param == 'status'):
        if(str(value) == '200'):
            value = 'OK('+str(value)+')'
        if(str(value) == '111'):
            value = 'ISSUE('+str(value)+')'
    keys = get_keys()
    if(api_id in keys):
        api_db.hmset(api_id,{param:value})


