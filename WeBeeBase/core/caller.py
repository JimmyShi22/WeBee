import math
import threading
import time
import heart
import globalVal
global globalVal

##
def atomic_call_lock():
    return threading.Lock()

def atomic_call(mutex, func):
    ret = None
    if mutex.acquire():
        ret = func()
        mutex.release()
    return ret


#call func at cyc time
def clock_call(func, milli_cyc):
    curr = curr_milli_time()
    expires = math.ceil(curr / float(milli_cyc)) * float(milli_cyc) - curr
    def call_func():
        time.sleep(expires / 1000)
        func()
    timer = threading.Timer(0, call_func)
    timer.start()


#cycle call
def cycle_call(func, milli_cyc):
    while True:
        time.sleep(float(milli_cyc) / 1000)
        func()


#mult thread call
class MyThread(threading.Thread):
    func = None

    def set_func(self, f):
        global func
        func = f

    def run(self):
        func()

def thread_call(func):
    t = MyThread()
    t.set_func(func)
    t.start()


##
def curr_milli_time():
    return math.ceil(time.time() * 1000)

def ptime():
    print int(curr_milli_time())