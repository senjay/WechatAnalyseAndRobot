import wxpy
import openpyxl
import os

class DataStorage:

    def __init__(self,bot,qlist) -> None:
        super().__init__()
        self.msgtype='获取好友信息'
        self.qlist=qlist
        self.bot = bot
        self.friend_all = self.bot.friends()
        self.loginName = self.friend_all[0].raw.get('NickName')
        self.createDir()

    def findFriendList(self):
        msg='正在获取好友信息\n\n'+'*' * 30 + '\n'
        self.qlist.put([self.msgtype,msg])
        self.qlist.join()
        lis=[]
        for a_friend in self.friend_all[1:]:
            UserName= a_friend.raw.get('UserName',None)
            NickName = a_friend.raw.get('NickName',None)
            RemarkName=a_friend.raw.get('RemarkName',None)
            Sex = a_friend.raw.get('Sex',None)
            Sex ={1:"男",2:"女",0:"未设置"}.get(a_friend.raw.get('Sex',None),None)
            City = a_friend.raw.get('City',None)
            Province = a_friend.raw.get('Province',None)
            Signature = a_friend.raw.get('Signature',None)
            #HeadImgUrl = a_friend.raw.get('HeadImgUrl',None)
            HeadImgUrl=self.saveHeadImg(UserName)
            list_0=[UserName,NickName,RemarkName,Sex,Province,City,Signature,HeadImgUrl,'空','空']#给ishuman headtag留空
            lis.append(list_0)
        msg='好友信息获取完毕\n\n'+'*' * 30 + '\n'
        self.qlist.put([self.msgtype,msg])
        self.qlist.join()
        return lis



    def saveHeadImg(self,UserName):
        img = self.bot.core.get_head_img(userName=UserName)
        filename =  UserName + ".jpg"
        path=os.path.join(self.userheadimg,filename)
        try:
            with open(path, 'wb') as f:
                f.write(img)
        except Exception as e:
            print(repr(e))
        return os.path.abspath(path)

    def createDir(self):
        if os.path.exists('userdata') != True:
            os.mkdir('userdata')
        self.userdir=os.path.join('userdata',self.loginName)
        self.userheadimg = os.path.join('userdata', self.loginName, 'headImg')
        if os.path.exists(self.userdir) != True:
            os.mkdir(self.userdir)
        if os.path.exists(self.userheadimg) != True:
            os.mkdir(self.userheadimg)
        self.qlist.put([self.msgtype, '正在创建文件夹\n\n'+'*' * 30 + '\n'+'路径为:'+os.path.abspath(self.userdir)+'\n\n'+'*' * 30 + '\n'])
        self.qlist.join()


    def saveExcel(self,lis):
        wb=openpyxl.Workbook()
        sheet=wb.worksheets[0]
        row = ['UserName','NickName', 'RemarkName', 'Sex','Province','City','Signature','HeadImgUrl','IsHuman','HeadImgTags']
        sheet.append(row)
        for item in lis:
            sheet.append(item)
        savepath=os.path.join(self.userdir,'friend.xlsx')
        wb.save(savepath)
        self.qlist.put([self.msgtype, '好友信息保存完毕\n\n'+'*' * 30 + '\n'])
        self.qlist.join()

def getFriendData(bot,qlist):
    datastorage = DataStorage(bot, qlist)
    lis = datastorage.findFriendList()
    datastorage.saveExcel(lis)


