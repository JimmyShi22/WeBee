import config, requests, globalVal, threading
from core import caller

global globalVal

def post_peers(op, arguement):
    rets = []
    for peer in config.peers_url: #TODO: parallel it
        if peer != config.url:
            print 'POST to ' + peer+str(op)
            try:
                ret = requests.post(peer + str(op), json=arguement)
                rets.append(ret)
            except:
                print 'POST to ' + peer+str(op) + ' error'
                continue
    return rets

def get_peers(op):
    rets = []
    for peer in config.peers_url: #TODO: parallel it
        if peer != config.url:
            print 'GET ' + peer + str(op)
            try:
                ret = requests.get(peer+str(op))
                rets.append(ret)
            except:
                print 'GET' + peer + str(op) + ' error'
                continue
    return rets

def post_peers_cnt(op, arguement):
    rets = []
    for peer in config.peers_url: #TODO: parallel it
        if peer != config.url:
            print 'POST to ' + peer+str(op)
            try:
                #atomic add send cnt
                caller.atomic_call(globalVal.SEND_CNT_LOCK, send_cnt_add)

                ret = requests.post(peer + str(op), json=arguement)
                rets.append(ret)

                # atomic minus send cnt
                caller.atomic_call(globalVal.SEND_CNT_LOCK, send_cnt_minus)
            except:
                print 'POST to ' + peer+str(op) + ' error'

                # atomic minus send cnt
                caller.atomic_call(globalVal.SEND_CNT_LOCK, send_cnt_minus)
                continue
    return rets

def get_peers_cnt(op):
    rets = []
    for peer in config.peers_url: #TODO: parallel it
        if peer != config.url:
            print 'GET ' + peer + str(op)
            try:
                # atomic add send cnt
                caller.atomic_call(globalVal.SEND_CNT_LOCK, send_cnt_add)

                ret = requests.get(peer+str(op))
                rets.append(ret)

                #atomic minus send cnt
                caller.atomic_call(globalVal.SEND_CNT_LOCK, send_cnt_minus)
            except:
                print 'GET' + peer + str(op) + ' error'

                # atomic minus send cnt
                caller.atomic_call(globalVal.SEND_CNT_LOCK, send_cnt_minus)
                continue
    return rets

def send_cnt_add():
    globalVal.SEND_CNT += 1

def send_cnt_minus():
    globalVal.SEND_CNT -= 1