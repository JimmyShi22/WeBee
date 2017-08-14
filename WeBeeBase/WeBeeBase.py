from flask import Flask, jsonify, request, json
try:
    import cPickle as pickle
except ImportError:
    import pickle
import requests
import heart
from core import caller, req, uniform
from WeBeeBlock import WeBeeBlock

import config, globalVal

global globalVal

app = Flask(__name__)
globalVal.BLOCK_CHAIN = WeBeeBlock()
globalVal.SEND_CNT_LOCK = caller.atomic_call_lock()
globalVal.PRE_UNIFORM_CNT_LOCK = caller.atomic_call_lock()
globalVal.UNIFORM_HASH_BUFF_LOCK = caller.atomic_call_lock()
globalVal.BLOCK_CHAIN_LOCK = caller.atomic_call_lock()

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/heart_beat')
def heart_beat():
    return 'ok'

@app.route('/inputdata', methods=['POST'])
def insert():
    msgs = json.loads(request.data)
    if globalVal.RECV_IS_LOCK:
        globalVal.RECV_BUF.append(msgs)
        return '1'
    else:
        for msg in msgs:
            fid = int(msg['id'])
            value = int(msg['num'])
            def _insert():
                return globalVal.BLOCK_CHAIN.insert(fid, value)
            caller.atomic_call(globalVal.BLOCK_CHAIN_LOCK, _insert)
            #caller.thread_call(req.post_peers('insert_from_peer', msg))
        req.post_peers_cnt('insert_from_peer', {'data': unicode(pickle.dumps(msgs), "utf-8")})
        return '1'

@app.route('/insert_from_peer', methods=['POST'])
def insert_from_peer():
    msgs = pickle.loads(request.json.get('data').encode("utf-8"))
    for msg in msgs:
        fid = int(msg['id'])
        value = int(msg['num'])

        def _insert():
            return globalVal.BLOCK_CHAIN.insert(fid, value)

        caller.atomic_call(globalVal.BLOCK_CHAIN_LOCK, _insert)
        # caller.thread_call(req.post_peers('insert_from_peer', msg))
    return 'ok'


@app.route('/modifydata', methods=['POST'])
def modify():
    msgs = json.loads(request.data)
    while globalVal.RECV_IS_LOCK:
        None
    for msg in msgs:
        fid = int(msg['id'])
        value = int(msg['num'])
        def _modify():
            return globalVal.BLOCK_CHAIN.modify(fid, value)
        caller.atomic_call(globalVal.BLOCK_CHAIN_LOCK, _modify)
        #caller.thread_call(req.post_peers('insert_from_peer', msg))

    return '1'

@app.route('/killpid')
def kill():
    caller.atomic_call(globalVal.BLOCK_CHAIN_LOCK, globalVal.BLOCK_CHAIN.deleteall)
    return '1'


@app.route('/getpid', methods=['POST'])
def getpid():
    return json.dumps(globalVal.BLOCK_CHAIN.get_block())

@app.route('/pre_uniform', methods=['POST'])
def pre_uniform():
    peer_url = request.json.get('url')

    def until_send_finish():
        #lock receive
        globalVal.RECV_IS_LOCK = True

        while globalVal.SEND_CNT > 0:
            None
        try:
            requests.get(peer_url)
        except:
            print 'send pre_uniform_back() error '
            pass

    caller.thread_call(until_send_finish)
    return 'ok'


@app.route('/pre_uniform_confirm', methods=['GET'])
def pre_uniform_confirm():
    def _minus():
        globalVal.PRE_UNIFORM_CNT -= 1
    caller.atomic_call(globalVal.PRE_UNIFORM_CNT_LOCK, _minus)
    return 'ok'

@app.route('/get_hash', methods=['POST'])
def get_hash():
    peer_url = request.json.get('url')
    res = globalVal.BLOCK_CHAIN.calc_hash()

    try:
        requests.post(peer_url, json={'url': config.url, 'hash': res})
    except:
        print 'get_hash send to main error'
        pass
    return 'ok'

@app.route('/get_hash_back', methods=['POST'])
def get_hash_back():
    msg = request.json
    def _append():
        globalVal.UNIFORM_HASH_BUFF.append(msg)
    caller.atomic_call(globalVal.UNIFORM_HASH_BUFF_LOCK, _append) # TODO: check msg is passed correctly
    return 'ok'

@app.route('/get_recover_chain_data', methods=['GET'])
def get_recover_chain_data():
    all_data =  globalVal.BLOCK_CHAIN.get_alldata()  #TODO:check it can pass obj
    return json.dumps(all_data)

@app.route('/recover_chain_data_all',methods=['POST'] )
def recover_chain_data_all():
    msg = request.json
    print msg.get('data')
    data = pickle.loads(msg.get('data').encode("utf-8"))
    print data
    #data = eval(msg.get('data'))
    globalVal.BLOCK_CHAIN.recover(data)
    globalVal.BLOCK_CHAIN.confirm_block()
    return 'ok'

@app.route('/confirm_block' ,methods=['GET'] )
def confirm_block():
    globalVal.BLOCK_CHAIN.confirm_block()
    return 'ok'

@app.route('/after_confirm', methods=['GET'])
def after_confirm():
    globalVal.RECV_IS_LOCK = False
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
    return 'ok'



if __name__ == '__main__':
    #caller.thread_call(heart.start_beat)
    caller.thread_call(uniform.start_uniform)
    app.run(host='0.0.0.0', port=config.port)
    print 'beat'
    heart.heart_beat()


