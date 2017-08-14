import time
import globalVal, requests, config
from core import caller
global globalVal

def check_peers():

    rets = []
    has_pre = False
    is_main = False
    peers_num = 1
    for peer in config.peers_url: #TODO: parallel it
        if peer == config.url:
            if has_pre == False:
                is_main = True
                print 'MAIN ' + peer
        else:
            print 'GET ' + peer+'heart_beat'
            try:
                resp = requests.get(peer+'heart_beat')
                if resp.status_code == requests.codes.ok:
                    has_pre = True
                    peers_num += 1;
            except:
                continue
    globalVal.IS_MAIN = is_main
    globalVal.PEERS_NUM = peers_num

def heart_beat():
    print
    print '----heart beat----(' + str(globalVal.HEART_BEAT_CNT) + ')'
    globalVal.HEART_BEAT_CNT += 1
    print 'URL ' + config.url
    print 'IS main ' + str(globalVal.IS_MAIN)
    print 'PEER NUM ' + str(globalVal.PEERS_NUM)

    check_peers()
    #print result
    print '----------------BLOCK CHAIN---------------------'
    try:
        globalVal.BLOCK_CHAIN.dataprint()
    except:
        print 'some error happend'
        pass
    print '------------------------------------------------'

def start_beat():
    time.sleep(config.time_before_start)
    caller.cycle_call(heart_beat, config.heart_beat_expires)