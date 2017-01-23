import ConfigParser
from slacker import Slacker
import time
import yaml
import urllib
import requests
import json
import redis_db
import socket

config = ConfigParser.ConfigParser()
config.read('slacker_data.ini')
slacker_token = config.get('Slacker','token')
slack = Slacker(slacker_token)


down_time = {}

def get_data():
    f = open('apis.yml','r')
    cfg = yaml.load(f)
    f.close()
    return cfg

def fetch_thing(url, params, method,timeout):
    socket.setdefaulttimeout(timeout)
    params = urllib.urlencode(params)
    if method=='POST':
        f = urllib.urlopen(url, params)
    else:
        f = urllib.urlopen(url+'?'+params)
    return yaml.safe_load(json.dumps(json.loads(f.read())))

def get_status(url,method,time_out):
    s_code = 0
    if(method == 'POST'):
        try:
            r = requests.post(url, timeout = time_out)
            s_code = r.status_code
        except:
            s_code = 111
    else:
        try:
            r = requests.get(url, timeout = time_out)
            s_code = r.status_code
        except:
            s_code = 111
    return s_code
        

def get_params(api,mode):
    result = []
    keys = api.keys()
    for values in keys:
        if mode in values:
            result.append(values)
    return result

def verify_match_old(dict1,dict2):
    keys = dict1.keys()
    flag = 0
    for i in keys:
        if(str(dict1[i]) != str(dict2[i])):
            #print '1',dict1[i]
            #print '2',dict2[i]
            flag = 1
            break
    print 'flag : ',flag
    return flag
def verify_match(d1,d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    same = set(o for o in intersect_keys if d1[o] == d2[o])
    if(d1_keys == same and len(modified.keys()) == 0):
        return (0,modified)
    else:
        return (1,modified)


def get_string(dict1,dict2):
    message1 = ''
    message2 = ''
    keys = dict1.keys()
    for i in keys:
        message2 += str(i) + ' : '
        try:
            message2 += dict2[i] + '\n'
        except:
            message2 += 'No value' + '\n'
        message1 += str(i) + ' : '
        message1 += str(dict1[i]) + '\n'
    return [message1,message2]

def slack_message(maintainer,message):
    try:
        slack.chat.post_message(channel=maintainer, text=message, username='Kingdom',icon_url='https://s28.postimg.org/6sxgjs4jh/king.png')
    except:
        print 'Unable To send message via slack'
        print 'Printing on console'
        print message

def notify_developer_url(status_code_c,status_code_p,endpoint,method,maintainer):
    if(status_code_c == 200):
        message='\nSite Is UP\nURL: '+str(endpoint)+'\nMethod :'+method+'\n\nStatus Code(current): 200\nStatus Code(Previous): '+str(status_code_p)
        slack_message(channel=maintainer, text=message, username='Kingdom',icon_url='https://s28.postimg.org/6sxgjs4jh/king.png')
    else:
        message='\nSite is having ISSUE\nURL: '+str(endpoint)+'\nMethod: '+method+'Status Code(Current):'+str(status_code_c)+'\nStatus Code(Previous):'+str(status_code_p)
        slack_message(maintainer,message)

def notify_developer_result(name,api_id,message1,maintainer,status):
    if(status == 'no'):
        message = 'Variation in result was detected\nNAME: '+name+'\n API ID:' + str(api_id) + '\n in : ' + str(message1)
        slack_message(maintainer,message)
    else:
        message = 'Variation in result was rectified\nNAME '+name+'\n API ID: ' + str(api_id)
        slack_message(maintainer,message)

def manage_down(api_id,current_time):
    print 'in manage down'
    keys = down_time.keys()
    if(str(api_id) in keys):
        down_time[str(api_id)][0] = current_time
    else:
        down_time[str(api_id)] = [current_time,0]

def manage_up(api_id,current_time):
    print 'in manage up'
    keys = down_time.keys()
    if(str(api_id) in keys):
        down_time[str(api_id)][1] += current_time - down_time[str(api_id)][0]
    else:
        down_time[str(api_id)] = [0,0]

def check_results(api,timeout,current_time):
    name = api['name']
    try:
        status_code = get_status(api['endpoint'],api['method'],timeout)
    except:
        status_code = 111
    if(status_code != 200):
        if(('200' in api['status']) or ('not available' in api['status'])):
            manage_down(api['id'],current_time)
        #if(str(api['status']) == str(status_code)):
        if(str(status_code) in str(api['status'])):
            pass
        else:
            redis_db.change_value(api['id'],'status',status_code)
            redis_db.change_value(api['id'],'result','not available')
            notify_developer_url(status_code,api['status'],api['endpoint'],api['method'],api['maintainer'])
            #manage_down(api['id'],current_time)
    else:
        if(str(status_code) not in str(api['status'])):
            redis_db.change_value(api['id'],'status',status_code)
            notify_developer_url(status_code,api['status'],api['endpoint'],api['method'],api['maintainer'])
            manage_up(api['id'],current_time)
        if(api['payload'] != ''):
            response = fetch_thing(api['endpoint'],yaml.safe_load(api['payload']),api['method'],timeout)
            answer , mismatch = verify_match(yaml.safe_load(api['output']),response)
            if(answer == 1):
                if(api['result'] == 'mismatch'):
                    pass
                elif(api['result'] == 'match' or api['result'] == 'not available'):
                    redis_db.change_value(api['id'],'result','mismatch')
                    notify_developer_result(name,api['id'],mismatch,api['maintainer'],'no')
            else:
                if(api['result'] == 'mismatch' or api['result'] == 'not available'):
                    redis_db.change_value(api['id'],'result','match')
                    notify_developer_result(name,api['id'],mismatch,api['maintainer'],'yes')

def update_percentage(current_time,apis,timer_start):
    keys = down_time.keys()
    total_time = current_time - timer_start
    for api in apis:
        keys1 = redis_db.get_keys()
        if(str(api['id']) in keys and api['id'] in keys1):
            if(('200' in api['status']) or ('not available' in api['status'])):
                print 'in condtn one for api: ' + api['id']
                up_time = total_time - down_time[api['id']][1]
                percentage = int((up_time/total_time)*100)
                print str(percentage) + '%'
                redis_db.change_value(api['id'],'efficiency',percentage)
            else:
                print 'in condtn two for api: ' + api['id']
                up_time = total_time -(down_time[api['id']][1] + (current_time - down_time[api['id']][0]))
                print 'stored current time :' + str(down_time[api['id']][0])
                print 'actual current time :' + str(current_time)
                print 'uptime :' + str(up_time)
                print 'downtime :' + str((down_time[api['id']][1] + (current_time - down_time[api['id']][0])))
                percentage = int((up_time/total_time)*100)
                print str(percentage) + '%'
                redis_db.change_value(api['id'],'efficiency',percentage)


def modify_downlist():
    keys1 = redis_db.get_keys()
    keys2 = down_time.keys()
    for key in keys2:
        if(key in keys1):
            pass
        else:
            del(down_time[key])


def main_loop():
    timeout = 5
    timer_start = time.time()
    while(True):
        modify_downlist()
        current_time = time.time()
        master_list = redis_db.get_value()
        for api in master_list:
            try:
                print 'checking api ID: ',api['id']
                check_results(api,timeout,current_time)
            except:
                print 'Network issue maybe'
        print down_time
        update_percentage(current_time,master_list,timer_start)
        print 'going for sleep'
        time.sleep(10)

main_loop()

