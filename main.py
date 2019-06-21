import wx
from wxpy import *
from WxRobot import Robot,Load
import threading
import time
import queue
import DataStorage
import Imgdetect
from multiprocessing import JoinableQueue
import AnalyseData
import os
import shutil
class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="微信控制", size=(800, 600))
        self.qlist = JoinableQueue()
        self.bot=None
        self.threadanalyse=None
        self.threadarobot=None
        panel = wx.Panel(self)
        self.a=panel
        self.Center()
        vbox = wx.BoxSizer(wx.VERTICAL)
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        box3=wx.BoxSizer(wx.HORIZONTAL)
        self.btn_Login= wx.Button(panel, label="登录", id=1)
        self.btn_Analyanse = wx.Button(panel, label="数据分析", id=2)
        self.btn_Robot = wx.Button(panel, label="机器人", id=3)
        self.btn_Logout=wx.Button(panel, label="退出登录", id=4)
        self.btn_Cleartext = wx.Button(panel, label="清理界面", id=5)
        self.btn_Clearfile = wx.Button(panel, label="清除文件", id=6)
        self.control_txt = wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_READONLY,size=(700,600) )
        box1.Add(self.btn_Login,proportion=1,flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,border=1)
        box1.Add(self.btn_Analyanse,proportion=1,flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,border=1)
        box1.Add(self.btn_Robot,proportion=1,flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,border=1)
        box1.Add(self.btn_Logout, proportion=1, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=1)
        box3.Add(self.btn_Cleartext, proportion=1, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=1)
        box3.Add(self.btn_Clearfile, proportion=1, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=1)
        box2.Add(self.control_txt,flag=wx.ALL|wx.EXPAND)
        vbox.Add(box1,proportion=1,flag=wx.EXPAND|wx.ALL,border=20)
        vbox.Add(box3, proportion=1, flag=wx.EXPAND | wx.ALL, border=20)
        vbox.Add(box2,proportion=2,flag=wx.ALL|wx.ALIGN_CENTER,border=0)
        self.Bind(wx.EVT_BUTTON,self.OnClicked,id=1,id2=6)
        panel.SetSizer(vbox)

    def getDataAndAnalyse(self,bot,qlist):
        username = bot.friends()[0].raw.get('NickName')
        dir = os.path.join('userdata', username)
        if os.path.exists(dir):
            qlist.put(['获取好友信息','检测到好友信息文件已经存在\n\n'+'*' * 30 + '\n'])
            qlist.join()
        else:
            DataStorage.getFriendData(bot,qlist)
            qlist.put(['获取好友信息','正在检测图片信息，请耐心等待\n\n'+'*' * 30 + '\n'])
            qlist.join()
            Imgdetect.getHeadImgContentByThread(username,20)
            qlist.put(['获取好友信息', '图片检测完毕\n\n' + '*' * 30 + '\n'])
            qlist.join()
        qlist.put(['获取好友信息','开始生成图表\n\n'+'*' * 30 + '\n'])
        qlist.join()
        AnalyseData.analyseAll(username)
        qlist.put(['获取好友信息', '图表生成完毕\n\n' + '*' * 30 + '\n'+'路径为:'+os.path.join('userdata',username,'result.html')+'\n\n'+'*' * 30 + '\n'])
        qlist.join()
        os.system('"E:/Firefox/firefox.exe" '+os.path.join('userdata',username,'result.html'))
        # import webbrowser
        # webbrowser.open(os.path.join('userdata',username,'result.html'))

    def showControl_txt(self):
        send_msg_count=0
        while True:
            if not self.qlist.empty():
                queuemsg=self.qlist.get()
                if queuemsg[0]=='管理员':
                    self.control_txt.AppendText(queuemsg[1])
                    self.control_txt.AppendText('*'*30+'\n')
                if queuemsg[0]=='获取好友信息':
                    self.control_txt.AppendText(queuemsg[1])
                self.qlist.task_done()
            try:
                if  self.bot is not None and self.bot.alive and hasattr(self.bot,'is_record_send_msg') and self.bot.is_record_send_msg:
                    sent_msgs = self.bot.messages.search(sender=self.bot.self)
                    if len(sent_msgs)>send_msg_count:
                        send_msg_count+=1
                        content=sent_msgs[len(sent_msgs)-1].text
                        receiver=str(sent_msgs[len(sent_msgs)-1].receiver)
                        self.control_txt.AppendText('发送给'+receiver+':\n'+content+'\n\n')
                        self.control_txt.AppendText('*' * 30 + '\n')
            except:
                pass

    def OnClicked(self, event):
        id = event.GetId()
        threading.Thread(target=self.showControl_txt).start()
        if id == 1:
            if self.checkLoginStatus()==False:
                self.bot=Bot(cache_path=True)
                self.control_txt.AppendText("登录成功\n")
                self.control_txt.AppendText('*' * 30 + '\n')
            else:
                self.messageBox("已经登录")
        elif id==2:
            if self.checkLoginStatus() == True:
                if  self.threadanalyse is None or self.threadanalyse.is_alive() ==False:
                    self.threadanalyse=threading.Thread(target=self.getDataAndAnalyse,args=(self.bot,self.qlist,))
                    self.threadanalyse.start()
                else:
                    self.messageBox("当前任务还未完成")
            else:
                self.messageBox("请先登录")
        elif id==3:
            if self.checkLoginStatus() == True:
                if  self.threadarobot  is None  or self.threadarobot.is_alive() ==False:
                    self.threadarobot =threading.Thread(target=Robot.RunRobot, args=(self.bot, self.qlist,))
                    self.threadarobot.start()
                    time.sleep(3)
                    self.control_txt.AppendText( Load.botStatusDetail(self.bot)+"\n\n")
                    self.control_txt.AppendText('*' * 30 + '\n')

                else:
                    self.messageBox("您已经启动机器人")
            else:
                self.messageBox("请先登录")
        elif id==4:
            if self.checkLoginStatus()==True:
                self.bot.logout()
                self.control_txt.AppendText("退出登录\n")
                self.control_txt.AppendText('*' * 30 + '\n')
            else:
                self.messageBox("您还未登录")

        elif id==5:
            self.control_txt.Clear()
        elif id==6:
            if self.checkLoginStatus()==True:
                username=self.bot.friends()[0].raw.get('NickName')
                dir=os.path.join('userdata', username)
                if os.path.exists(dir):
                    shutil.rmtree(dir)
            if  os.path.exists('wxpy.pkl'):
                os.remove('wxpy.pkl')
            self.control_txt.AppendText("文件及记录清除完成\n\n")
            self.control_txt.AppendText('*' * 30 + '\n')

    def checkLoginStatus(self):
        if self.bot is None or self.bot.alive==False:
            return False
        return True

    def messageBox(self,string):
        dlg = wx.MessageDialog(None, string, u"很抱歉", wx.YES_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.Close(True)
        dlg.Destroy()

    def Destroy(self):
        super().Destroy()
        self.bot.logout()
        return True


class App(wx.App):
    def OnInit(self):
        frame = MyFrame()
        frame.Show()
        return True

    def OnExit(self):
        return 0


if __name__ == '__main__':
    app = App()
    app.MainLoop()
