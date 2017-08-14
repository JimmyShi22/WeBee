import time, requests, json
try:
    import cPickle as pickle
except ImportError:
    import pickle
import config, globalVal, heart
from core import req, caller

global globalVal

def uniform():
    heart.heart_beat()
    #heart.check_peers()
    if globalVal.IS_MAIN == False:
        return

    print '----------uniform------------(' +  str(globalVal.UNIFORM_CNT) + ')'
    globalVal.UNIFORM_CNT += 1

    #
    # pre uniform
    #
    globalVal.PRE_UNIFORM_CNT = globalVal.PEERS_NUM - 1

    #send pre uniform signal
    globalVal.RECV_IS_LOCK = True
    req.post_peers('pre_uniform', {'url': config.url + 'pre_uniform_confirm'})

    #wait pre uniform confirm, loop until all send finish
    while globalVal.SEND_CNT > 0:
        None

    # wait pre uniform confirm, loop until all peers confirm
    while globalVal.PRE_UNIFORM_CNT > 0:
        None

    #
    # uniform
    #
    globalVal.UNIFORM_HASH_BUFF = []
    req.post_peers('get_hash', {'url': config.url + 'get_hash_back'})
    this_hash = globalVal.BLOCK_CHAIN.calc_hash()

    print 'loop until all hash send back'
    #loop until all hash send back
    while len(globalVal.UNIFORM_HASH_BUFF) < globalVal.PEERS_NUM - 1:
        None

    # get most freq hash
    hash_array = [this_hash]
    for msg in globalVal.UNIFORM_HASH_BUFF:
        hash_array.append(msg.get('hash'))
    def countMax(arry):
        import collections
        max = collections.Counter(arry).most_common()[0][0]
        return max

    most_hash = countMax(hash_array)

    #recover incoreccted process
    for msg in globalVal.UNIFORM_HASH_BUFF:
        if msg.get('hash') != most_hash:
            print 'diff hash'
            print msg
            globalVal.UNIFORM_DIFF_HASH_URLS.append(msg.get('url'))
        else:
            requests.get(msg.get('url') + 'confirm_block')

    incorrect_cnt = len(globalVal.UNIFORM_DIFF_HASH_URLS)
    if this_hash != most_hash:
        incorrect_cnt += 1

    if incorrect_cnt >= (globalVal.PEERS_NUM + 1) / 2:
        print 'ERROR: Most of peers are incorrect !!!!!!'

    recover_all_data = None
    if len(globalVal.UNIFORM_DIFF_HASH_URLS) > 0 or this_hash != most_hash:
        for msg in globalVal.UNIFORM_HASH_BUFF:
            if msg.get('hash') == most_hash:
                try:
                    res = requests.get(msg.get('url')+'get_recover_chain_data')
                    recover_all_data = json.loads(res.text)
                    break
                except:
                    print 'get recover data from ' + msg.get('url') + 'failed. Try another'
                    continue

    print recover_all_data
    for url in globalVal.UNIFORM_DIFF_HASH_URLS:
        try:
            requests.post(url + 'recover_chain_data_all', json={'data': unicode(pickle.dumps(recover_all_data), "utf-8")})
        except:
            print 'recover process ' + url + ', connect failed'
            continue

    # for url in globalVal.UNIFORM_DIFF_HASH_URLS:
    #     try:
    #         requests.get(url + 'confirm_block')
    #     except:
    #         print 'confirm after recover connect failed'
    #         continue
    globalVal.UNIFORM_DIFF_HASH_URLS = []

    if this_hash != most_hash:
        globalVal.BLOCK_CHAIN.recover(recover_all_data)
    globalVal.BLOCK_CHAIN.confirm_block()

    #
    # after uniform
    #
    globalVal.RECV_IS_LOCK = False
    req.get_peers('after_confirm')

    for msgs in globalVal.RECV_BUF:
        for msg in msgs:
            fid = int(msg['id'])
            value = int(msg['num'])
            def _insert():
                return globalVal.BLOCK_CHAIN.insert(fid, value)
            caller.atomic_call(globalVal.BLOCK_CHAIN_LOCK, _insert)
        #req.post_peers_cnt('insert_from_peer', json.dumps(msgs))
        req.post_peers_cnt('insert_from_peer', {'data': unicode(pickle.dumps(msgs), "utf-8")})

    globalVal.RECV_BUF = []

    print '----------------BLOCK CHAIN---------------------'
    try:
        globalVal.BLOCK_CHAIN.dataprint()
    except:
        print 'some error happend'
        pass
    print '------------------------------------------------'


def uni():
    print 'uni'


def start_uniform():
    time.sleep(config.time_before_start)
    caller.cycle_call(uniform, config.uniform_expires)