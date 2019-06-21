import requests
import base64
import json
import time
import random
import hmac, hashlib
import binascii
import pandas as pd
import os
import numpy
import threading

user_agent_list = ['Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6721.400 QQBrowser/10.2.2243.400',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6721.400 QQBrowser/10.2.2243.400',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15']

class Imgdetect:
    def __init__(self) -> None:
        super().__init__()
        #腾讯优图的key,需自行申请
        self.AppID = '*****'
        self.SecretID = '**********'
        self.SecretKey = '**********'
        self.UserId = '**********'

    #生成优图接口签名算法
    """
    u=10000&a=2011541224&k=AKID2ZkOXFyDRHZRlbPo93SMtzVY79kpAdGP&e=1432970065&t=1427786065&r=270494647&f=
    u为开发者创建应用时的QQ号
    a为用户的AppID
    k为用户的SecretID
    t为当前时间戳，是一个符合UNIX Epoch时间戳规范的数值，单位为秒
    e为此签名的凭证有效期，是一个符合UNIX Epoch时间戳规范的数值，单位为秒，e应大于t，生成的签名在 t 到 e 的时间内都是有效的。如果是0，则生成的签名只有再t的时刻是有效的
    r为随机串，无符号10进制整数，用户需自行生成，最长10位
    f为空
    使用 HMAC-SHA1 算法对请求进行签名。
    签名串需要使用 Base64 编码。
    根据签名方法Sign= Base64(HMAC-SHA1(SecretKey, orignal) + original)，orignal使用HMAC-SHA1算法进行签名，
    然后将orignal附加到签名结果的末尾，再进行Base64编码，得到最终的sign。 
    """
    def createSign(self):
        expired = int(time.time()) + 2592000
        puserid = ''
        if self.UserId != '':
            puserid = self.UserId

        now = int(time.time())
        rdm = random.randint(0, 999999999)

        plain_text = 'a=' + self.AppID + '&k=' + self.SecretID + '&e=' + str(expired) + '&t=' + str(now) + '&r=' + str(
            rdm) + '&u=' + puserid + '&f='
        bin = hmac.new(self.SecretKey.encode(), plain_text.encode(), hashlib.sha1)
        s = bin.hexdigest()
        s = binascii.unhexlify(s)
        s = s + plain_text.encode('ascii')
        signature = base64.b64encode(s).rstrip()  # 生成签名
        return signature


    def faceDetect(self,path):
        faceurl='http://api.youtu.qq.com/youtu/api/detectface'
        signature = self.createSign()
        headers = {
            'Host':'api.youtu.qq.com',
            'User-Agent': random.choice(user_agent_list),
            'Authorization': signature,
            'Content-Type': 'text/json'
        }
        imgdata = base64.b64encode(open(path, 'rb').read()).rstrip().decode('utf-8')
        post_data={
          "app_id": self.AppID,
          "image": imgdata
        }
        try:
            response=requests.post(url=faceurl,data=json.dumps(post_data),headers=headers,timeout=2)
            if response.status_code != 200:
                print({'httpcode': response.status_code, 'errorcode': '', 'errormsg': '', "person_id": '',
                        "session_id ": ''})
                return -1
            answer = json.loads(response.content.decode(), encoding='utf-8', )
            if answer['errormsg'] == 'OK':
                return '是'
            return '否'
        except:
            return -1

    #返回图像标签，标签以list返回,置信度从高到低
    def tagsDectect(self,path):
       tagsurl='http://api.youtu.qq.com/youtu/imageapi/imagetag'
       signature = self.createSign()
       headers = {
           'Host': 'api.youtu.qq.com',
           'User-Agent':random.choice(user_agent_list),
           'Authorization': signature,
           'Content-Type': 'text/json'
       }
       imgdata = base64.b64encode(open(path, 'rb').read()).rstrip().decode('utf-8')
       post_data = {
           "app_id": self.AppID,
           "image": imgdata
       }
       try:
           response = requests.post(url=tagsurl, data=json.dumps(post_data), headers=headers, timeout=2)
           if response.status_code != 200:
               print({'httpcode': response.status_code, 'errorcode': '', 'errormsg': '', "person_id": '',
                      "session_id ": ''})
               return -1
           answer = json.loads(response.content.decode(), encoding='utf-8')['tags']
           answer.sort(key=lambda x: x['tag_confidence'], reverse=True)
           tags = [i['tag_name'] for i in answer]
           return tags
       except:
           return -1

def getHeadImgContent(username):
    imgdetect = Imgdetect()
    datas = pd.read_excel(os.path.join('userdata', username, 'friend.xlsx'))
    count = 0
    for index, data in datas.iterrows():
        url = data['HeadImgUrl']
        while True:
            answer = imgdetect.faceDetect(url)
            if answer == -1:
                continue
            datas.at[index, 'IsHuman'] = answer
            break
        while True:
            answer = imgdetect.tagsDectect(url)
            if answer == -1:
                continue
            datas.at[index, 'HeadImgTags'] = answer
            break
        count += 1
        print(count)
    datas.to_excel(os.path.join('userdata', username, 'friend.xlsx'), index=None)



#getHeadImgContent('神交')单线程版本
imgdetect = Imgdetect()
def threadBody(datas,dic):
    for index,url in datas.iteritems():
        while True:
            answer1 = imgdetect.faceDetect(url)
            if answer1 == -1:
                continue
            break
        while True:
            answer2 = imgdetect.tagsDectect(url)
            if answer2 == -1:
                continue
            break
        dic[index]=[answer1,answer2]
        print(index)

def threadRequests(username,threadnum):
    n=threadnum#线程数
    threads=[]
    dic={}
    datas = pd.read_excel(os.path.join('userdata', username, 'friend.xlsx'))
    datas=datas['HeadImgUrl']
    s=numpy.array_split(datas, n)
    for i in range(n):
        t=threading.Thread(target=threadBody,args=(s[i],dic))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    return dic

def writeReturn(dic,username):
    datas = pd.read_excel(os.path.join('userdata', username, 'friend.xlsx'))
    for i in range(len(datas)):
        datas.at[i, 'IsHuman'] = dic[i][0]
        datas.at[i, 'HeadImgTags'] = dic[i][1]
    datas.to_excel(os.path.join('userdata', username, 'friend.xlsx'), index=None)

def getHeadImgContentByThread(username,threadnum):
    dic=threadRequests(username,threadnum)
    writeReturn(dic,username)



