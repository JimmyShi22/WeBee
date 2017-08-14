import csv
import hashlib
filepath0='test.csv'
class WeBeeBlock():
    def __init__(self):
        self.filepath=filepath0
        self.hash=''
        self.sortdata=[]
        self.data={}
        self.sortblock=[]
        self.block={}
        self.fid_blockid={}
        self.blockhash={}
        self.blockmoney={}
        self.blockstate={}
        self.money=0
        self.nowblockid=0
    def insert(self,fid,value):
        if fid in self.fid_blockid:
            return False
        self.blockstate[self.nowblockid]=0
        self.fid_blockid[fid]=self.nowblockid
        self.block[fid]=value
        self.data[fid]=value
        return True
    def cacl_buffhash(self):
        if len(self.block)==0:return self.hash
        self.sortblock=list(sorted(self.block.items(), key=lambda x:x[0]))
        nowmoney=0
        nowstr=''
        for i in self.sortblock:
            nowmoney+=i[1]
            nowstr+=str(i[0])+'#'+str(i[1])+'#'
        if self.nowblockid==0:
            self.money=nowmoney
            self.hash=hashlib.sha256(nowstr.encode('utf-8')).hexdigest()
        else:
            self.money=self.blockmoney[self.nowblockid-1]+nowmoney
            self.hash=hashlib.sha256((self.blockhash[self.nowblockid-1]+nowstr).encode('utf-8')).hexdigest()
        self.blockmoney[self.nowblockid]=self.money
        self.blockhash[self.nowblockid]=self.hash
        return self.hash
    def calc_hash(self):
        if len(self.sortdata)==0 and len(self.block)==0:return ''
        self.hash=''
        self.money=0
        for i in range(self.nowblockid):
            self.blockstate[i]=1
            nowstr=''
            for j in self.sortdata[i]:
                self.money+=j[1]
                nowstr+=str(j[0])+'#'+str(j[1])+'#'
            self.blockmoney[i] = self.money
            self.blockhash[i]=hashlib.sha256((self.hash+nowstr).encode('utf-8')).hexdigest()
            self.hash = self.blockhash[i]
        if len(self.block)>0:
            self.blockstate[self.nowblockid]=0
            self.sortblock = list(sorted(self.block.items(), key=lambda x: x[0]))
            nowstr = ''
            for i in self.sortblock:
                self.money += i[1]
                nowstr += str(i[0]) + '#' + str(i[1]) + '#'
            self.blockhash[self.nowblockid] = hashlib.sha256((self.hash + nowstr).encode('utf-8')).hexdigest()
            self.blockmoney[self.nowblockid] = self.money
            self.hash = self.blockhash[self.nowblockid]
        return self.hash
    def confirm_block(self):
        if len(self.block)==0:return False
        self.sortdata.append(self.sortblock)
        a=list(sorted(self.data.items(), key=lambda x: x[0]))
        b=csv.writer(open(self.filepath,mode='w'))
        b.writerows(a)
        self.sortblock=[]
        self.block.clear()
        self.blockstate[self.nowblockid]=1
        self.nowblockid += 1
        return True
    def modify(self,fid,value):
        if self.data[fid]==value:return None
        a = list(sorted(self.data.items(), key=lambda x: x[0]))
        b = csv.writer(open(self.filepath, mode='w'))
        b.writerows(a)
        for i in range(self.fid_blockid[fid],self.nowblockid+1):
            self.blockstate[i]=2
        for u,v in enumerate(self.sortdata[self.fid_blockid[fid]]):
            if v[0]==fid:
                self.sortdata[self.fid_blockid[fid]][u]=(fid,value)
                break
    def deletefid(self,fid):
        if fid not in self.data:return None
        self.data.pop(fid)
        for i in range(self.fid_blockid[fid],self.nowblockid+1):
            self.blockstate[i]=2
        for u,v in enumerate(self.sortdata[self.fid_blockid[fid]]):
            if v[0]==fid:
                self.sortdata[self.fid_blockid[fid]]=self.sortdata[self.fid_blockid[fid]][0:u]+self.sortdata[self.fid_blockid[fid]][u+1:-1]
                break
    def check(self):
        nowhash=''
        for u,v in enumerate(self.sortdata):
            nowstr=''
            for j in v:
                nowstr+=str(j[0])+'#'+str(j[1])+'#'
            nowhash=hashlib.sha256((nowhash+nowstr).encode('utf-8')).hexdigest()
            if nowhash!=self.blockhash[u]:
                return u
        return -1
    def get_bloackhash(self,blockid):
        return self.blockhash[blockid]
    def get_block(self):
        sortdata=self.sortdata
        blockhash=self.blockhash
        blockstate = self.blockstate
        lenblock=self.nowblockid
        if len(self.block)>0:
            lenblock+=1
            self.cacl_buffhash()
            sortdata.append(self.sortblock)
            blockhash = self.blockhash
        returndata=[]
        for i in range(lenblock):
            a={}
            b=[]
            for j in sortdata[i]:
                c={}
                c['id']=j[0]
                c['num']=j[1]
                b.append(c)
            a['data']=b
            a['hash']=blockhash[i]
            a['state']=blockstate[i]
            returndata.append(a)
        return returndata
    def set_block(self,blockid,blockdata):
        datacopy=self.data
        for i in self.sortdata[blockid]:
            datacopy[i[0]]=i[1]
        return [self.sortdata[blockid],
                datacopy,
                self.fid_blockid,
                self.blockhash[blockid],
                self.blockmoney[blockid],
                self.blockstate[blockid],
                self.money]
    def get_alldata(self):
        return [self.sortdata,self.block]
    def recover(self,outdata):
        self.deleteall()
        [self.sortdata, self.block]=outdata
        self.nowblockid=len(self.sortdata)
        a=self.block
        self.block={}
        self.data={}
        self.fid_blockid={}
        for i in a:
            self.block[int(i)]=a[i]
            self.data[int(i)]=a[i]
            self.fid_blockid[int(i)]=self.nowblockid
        for u,v in enumerate(self.sortdata):
            for j in v:
                self.data[j[0]]=j[1]
                self.fid_blockid[j[0]]=u
        self.calc_hash()
        a = list(sorted(self.data.items(), key=lambda x: x[0]))
        b = csv.writer(open(self.filepath, mode='w'))
        b.writerows(a)
    def get_money(self):
        return self.money
    def get_nowblockid(self):
        return self.nowblockid
    def get_fid(self,fid):
        return self.data[fid]
    def get_fid_blockid(self,fid):
        return self.fid_blockid[fid]
    def deleteall(self):
        self.__init__()
        csv.writer(open(self.filepath, mode='w'))
    def get_hash(self):
        return self.hash
    def dataprint(self):
        print('self.hash',self.hash)
        print('self.sortdata',self.sortdata)
        print('self.data',self.data)
        print('self.sortblock',self.sortblock)
        print('self.block',self.block)
        print('self.fid_blockid',self.fid_blockid)
        print('self.blockhash',self.blockhash)
        print('self.blockmoney',self.blockmoney)
        print('self.blockstate',self.blockstate)
        print('self.money',self.money)
        print('self.nowblockid',self.nowblockid)
        print('self.sortblock',self.sortblock)
# wb=WeBeeBlock()
# while(True):
#     print('''
#     1:insert(self,fid,value) 2:cacl_buffhash(self) 3:confirm_block(self)
#     4:modify(self,fid,value) 5:deletefid(self,fid) 6:calc_hash(self)
#     7:get_bloackhash(self,blockid) 8:get_block(self,blockid) 9:set_block(self,blockid,blockdata)
#     10:get_alldata(self) 11:recover(self,outdata) 12:get_money(self)
#     13:get_nowblockid(self) 14:get_fid(self,fid) 15:get_fid_blockid(self,fid)
#     16:deleteall(self) 17:get_hash(self) 18:dataprint(self) 19:check(self)
#     ''')
#     a=int(input())
#     if a == 0:break
#     elif a == 1:
#         print('insert(int(input), int(input))')
#         wb.insert(int(input()), int(input()))
#     elif a == 2:
#         print('wb.cacl_buffhash()')
#         print(wb.cacl_buffhash())
#     elif a == 3:
#         print('confirm_block()')
#         wb.confirm_block()
#     elif a == 4:
#         print('modify(int(input()),int(input()))')
#         wb.modify(int(input()),int(input()))
#     elif a == 5:
#         print('deletefid(int(input()))')
#         wb.deletefid(int(input()))
#     elif a == 6:
#         print('calc_hash()')
#         print(wb.calc_hash())
#     elif a == 7:
#         print('wb.get_bloackhash(int(input()))')
#         print(wb.get_bloackhash(int(input())))
#     elif a == 8:
#         print('wb.get_block(int(input()))')
#         print(wb.get_block(int(input())))
#     elif a==9:
#         print('set_block(wb.get_block(int(input())))')
#         wb.set_block(wb.get_block(int(input())))
#     elif a == 10:
#         print('wb.get_alldata()')
#         print(wb.get_alldata())
#     elif a == 11:
#         print('recover(wb.get_alldata())')
#         wb.recover(wb.get_alldata())
#     elif a == 12:
#         print('wb.get_money()')
#         print(wb.get_money())
#     elif a == 13:
#         print('wb.get_nowblockid()')
#         print(wb.get_nowblockid())
#     elif a == 14:
#         print('wb.get_fid(int(input()))')
#         print(wb.get_fid(int(input())))
#     elif a == 15:
#         print('wb.get_fid_blockid(int(input()))')
#         print(wb.get_fid_blockid(int(input())))
#     elif a == 16:
#         print('deleteall()')
#         wb.deleteall()
#     elif a == 17:
#         print('get_hash(self)')
#         print(wb.get_hash())
#     elif a == 18:
#         print('dataprint(self)')
#         wb.dataprint()
#     elif a == 19:
#         print('check(self)')
#         print(wb.check())
#     elif a == 20:
#         print('get_block(self')
#         print(wb.get_block())