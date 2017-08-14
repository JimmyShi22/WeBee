from flask import Flask
from flask import request
from flask_cors import *
import requests
import json
import random
app = Flask(__name__)
CORS(app,supports_credentials=True)

ipmap = {'ip1':'http://119.29.100.177:18088',
         'ip2':'http://119.29.100.177:18089',
         'ip3':'http://119.29.181.234:18088',
         'ip4':'http://119.29.181.234:18089',
         'ip5':'http://119.29.12.135:18088',
         'ip6':'http://119.29.12.135:18089',
         'ip7':'http://119.29.12.135:18090'}

ips = ['ip1','ip3','ip4','ip5','ip6','ip7']

ip_state = {'ip1':1,'ip2':1,'ip3':1,'ip4':1,'ip5':1,'ip6':1,'ip7':1}


def post(url, datas=None):
    headers = {'content-type': 'application/json'}
    response = requests.post(url,data=datas,headers=headers).content

    return response


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/inputdata', methods=['POST'])
def inputdata():
    flags = []
    raw_data = request.data
    if raw_data:
        print raw_data
    else:print '11111111'
    json_data = json.loads(raw_data)
    for item in json_data:
        data = json.dumps([item])
        url = ipmap[random.choice(ips)]
        url = url+'/'+'inputdata'
        flag = post(url,data)
        flags.append(flag)
    print flags
    flags = json.dumps(flags)
    return flags


@app.route('/modifydata', methods=['POST'])
def modifydata():
    raw_data = request.data
    json_data = json.loads(raw_data)
    ip_num = json_data['ip']
    url = ipmap[ip_num]
    url = url+'/'+'modifydata'
    data = json_data['data']
    data = json.dumps(data)
    try:
        post(url,datas=data)
    except:
        'none'
    return '1'


@app.route('/killpid', methods=['POST'])
def killpid():
    flags = []
    raw_data = request.data
    json_data = json.loads(raw_data)
    for item in json_data:
        ip_num = item['ip']
        url = ipmap[ip_num]
        ip_state[ip_num] = 0
        url = url+'/'+'killpid'
        data = {ip_num:'1'}
        data = json.dumps(data)
        flag = post(url,datas=data)
        flags.append(flag)
    flags = json.dumps(flags)
    return flags


@app.route('/startpid', methods=['POST'])
def startpid():

    raw_data = request.data
    json_data = json.loads(raw_data)
    for item in json_data:
        ip_num = item['ip']
        ip_state[ip_num] = 1
        # url = ipmap[ip_num]
        # url = url+'/'+'startpid'
        # data = {ip_num:'1'}
        # data = json.dumps(data)
        # post(url,datas=data)
    return '1'


###########################################
@app.route('/getpid', methods=['POST'])
def getid():
    return_data = {}
    balance = 0
    raw_data = request.data
    print raw_data
    json_data = json.loads(raw_data)
    ip_num = json_data[0]['ip']
    now_page = json_data[0]['page']
    if ip_state[ip_num] == 0:
        return_data = {'block_data':[{"data":[],'hash':'0','state':0}],'total_page':0,'balance':0}
        return_data = json.dumps(return_data)
        return return_data
    else:
        url = ipmap[ip_num]
        url = url+'/'+'getpid'
        try:
            data = post(url)
        except:
            data = json.dumps({'block_data':[{"data":[],'hash':'0','state':0}],'total_page':0,'balance':0})
            return data
        data = json.loads(data)
        print 'data',data
        for item in data:
            for block in item['data']:
                balance+=block['num']
        data_len = len(data)
        if data_len % 5 == 0:
            total_page = data_len / 5
        else:
            total_page = data_len / 5 + 1
        blockdata = data[now_page*5-5:now_page*5]
        return_data['block_data'] = blockdata
        return_data['total_page'] = total_page
        return_data['balance'] = balance
        print 'return_data',return_data
        return_data = json.dumps(return_data)
        return return_data


@app.route('/getpidcount', methods=['POST'])
def getcount():
    count_data = []
    return_data = {}
    raw_data = request.data
    json_data = json.loads(raw_data)
    ip_num = json_data[0]['ip']
    now_page = json_data[0]['page']
    url = ipmap[ip_num]
    url = url + '/' + 'getpid'
    try:
        pid_data = post(url)
    except:
        return_data = {'total_page':0,'count_data':[],'banlance':0}
        return_data = json.dumps(return_data)
        return return_data
    pid_data = json.loads(pid_data)
    for item in pid_data:
        count_data.extend(item['data'])
    data_len = len(count_data)
    if data_len % 10 == 0:
        total_page = data_len / 10
    else:
        total_page = data_len / 10 + 1

    balance = 0
    for item in count_data:
        balance+=item['num']
    # return_data = count_data[now_page:now_page+10]
    return_data['total_page'] = total_page
    return_data['count_data'] = count_data[now_page*10-10:now_page*10]
    return_data['balance'] = balance
    return_data = json.dumps(return_data)

    return return_data


@app.route('/isnormal', methods=['POST'])
def isnormal():
    # state = []
    # for ip in ips:
    #     url = ipmap[ip]
    #     url = url + '/' + 'isnormal'
    #     flag = post(url)
    #     ip_state = {ip:flag}
    #     state.append(ip_state)
    state = json.dumps([ip_state])
    return state


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8089,debug=True)
