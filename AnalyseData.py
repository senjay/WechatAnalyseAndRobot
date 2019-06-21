import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import jieba
import jieba.analyse
from snownlp import SnowNLP
import os
import json
import ast#用于转换字符串型list
from pyecharts.charts import Map,Page,Sunburst,Pie,WordCloud,Grid,Line,Bar,Scatter,Bar3D
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
import  random
from pyecharts import globals
from example.commons import Faker

# 中文乱码设置
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['font.family']='sans-serif'
# 设置x, y轴刻度字体大小
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['ytick.labelsize'] = 16
plt.style.use('ggplot')

class Analyse:
    def __init__(self,username) -> None:
        super().__init__()
        self.username=username
        self.df_friends = pd.read_excel(os.path.join('userdata',self.username,'friend.xlsx'))
        self.page = Page(page_title='分析结果',interval=20, layout=Page.SimplePageLayout)

    def analyseSex(self):
        sex_count = self.df_friends.groupby('Sex')['Sex'].count()
        sex_count_order = sex_count.sort_values(ascending=False)
        pie=(
            Pie().add(
            "",
            [list(z) for z in zip(['男', '女', '未设置'], sex_count_order.values.tolist())],
            center=["35%", "50%"],
        ).set_colors([self.createRandomColor(),self.createRandomColor(),self.createRandomColor()])
            .set_global_opts(
            title_opts=opts.TitleOpts(title="性别分布"),
            legend_opts=opts.LegendOpts(pos_left="80%",orient="vertical"),
        ).set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}人，占{d}%"),)
        )
        return pie

    def analyseGeo(self):
        prv_cnt = self.df_friends.groupby('Province', as_index=True)['Province'].count().sort_values()
        provice=prv_cnt.index.tolist()
        values = prv_cnt.values.tolist()

        map1 = (
            Map().add("",[list(z) for z in zip(provice, values)], "china").set_global_opts(
            title_opts=opts.TitleOpts(title="好友全国分布"),
            visualmap_opts=opts.VisualMapOpts(max_=200,is_piecewise=True),#, is_piecewise=True分段
        )
        )
        prv_max=provice[-1]
        city_cnt=self.df_friends[self.df_friends['Province']==prv_max].groupby('City', as_index=True)['City'].count().sort_values()
        city = city_cnt.index.map(lambda x:x+'市').tolist()#末尾要+个 市才会识别
        values1 = city_cnt.values.tolist()
        map2 = (
            Map().add("", [list(z) for z in zip(city, values1)],prv_max).set_global_opts(
            title_opts=opts.TitleOpts(title="好友最多省份城市分布"),
            visualmap_opts=opts.VisualMapOpts(),  # , is_piecewise=True分段
        )
        )
        return [map1,map2]

    def analyseSignature(self):
        words = []
        signatures = self.df_friends['Signature']
        for signature in signatures.values:
            signature = str(signature)
            if signature != 'nan':
                temp = jieba.analyse.extract_tags(signature, 5)
                if len(temp) != 0:
                    words.extend(temp)

        dic = {}
        for word in words:
            if word not in dic.keys():
                dic[word] = 1
            else:
                dic[word] += 1
        values=list(dic.items())
        wc = (
            WordCloud().add("", values, word_size_range=[20, 100],
                             shape='diamond')
            .set_global_opts(title_opts=opts.TitleOpts(title="好友签名关键词分析"))
        )
        return  wc

    def analyseSignatureEmotion(self):
        signatures = self.df_friends[['Sex','Signature']]
        neutral={
             "name": "中性",
            "itemStyle": {"color": self.createRandomColor()},
            "children":[{
             "name": "男",
            "itemStyle": {"color": self.createRandomColor()},
            "children":[]
        },{
            "name": "女",
            "itemStyle": {"color": self.createRandomColor()},
            "children": []
        },{
            "name": "未设置",
            "itemStyle": {"color": self.createRandomColor()},
            "children": []
        }]
        }
        position={
            "name": "积极",
            "itemStyle": {"color": self.createRandomColor()},
            "children": [{
             "name": "男",
            "itemStyle": {"color": self.createRandomColor()},
            "children":[]
        },{
            "name": "女",
            "itemStyle": {"color": self.createRandomColor()},
            "children": []
        },{
            "name": "未设置",
            "itemStyle": {"color": self.createRandomColor()},
            "children": []
        }]
        }
        negative={
            "name": "消极",
            "itemStyle": {"color": self.createRandomColor()},
            "children": [{
             "name": "男",
            "itemStyle": {"color": self.createRandomColor()},
            "children":[]
        },{
            "name": "女",
            "itemStyle": {"color": self.createRandomColor()},
            "children": []
        },{
            "name": "未设置",
            "itemStyle": {"color": self.createRandomColor()},
            "children": []
        }]
        }
        unset={
            "name": "空",
            "itemStyle": {"color": self.createRandomColor()},
            "children": [{
             "name": "男",
            "itemStyle": {"color": self.createRandomColor()},
            "children":[]
        },{
            "name": "女",
            "itemStyle": {"color": self.createRandomColor()},
            "children": []
        },{
            "name": "未设置",
            "itemStyle": {"color": self.createRandomColor()},
            "children": []
        }]
        }
        for sex,signature in signatures.values:
            sex = str(sex)
            signature = str(signature)
            dictemp={
                 "name": signature if signature !='nan' else '空',
                "value":1,
                "itemStyle": {"color": self.createRandomColor()},
            }
            if signature=='nan':
                self.putEmotiomInSex(sex, unset['children'], dictemp)
            else:
                e=SnowNLP(signature).sentiments
                if(e>0.5):
                    self.putEmotiomInSex(sex,position['children'],dictemp)
                elif (e <0.5):
                    self.putEmotiomInSex(sex, negative['children'], dictemp)
                else:
                    self.putEmotiomInSex(sex, neutral['children'], dictemp)
        lst=[position,negative,neutral,unset]

        sun=(
            Sunburst(init_opts=opts.InitOpts())
            .add(
            "",
            data_pair=lst,
            highlight_policy="ancestor",
            radius=[0, "95%"],
            sort_="null",
            levels=[
                {},
                {
                    "r0": "15%",
                    "r": "35%",
                    "itemStyle": {"borderWidth": 2},
                    "label": {"rotate": "tangential"},
                },
                {"r0": "35%", "r": "70%", "label": {"align": "right"}},
                {
                    "r0": "70%",
                    "r": "72%",
                    "label": {"position": "outside", "padding": 3, "silent": False,"show":False},
                    "itemStyle": {"borderWidth": 3},
                },
            ],
        ).set_global_opts(title_opts=opts.TitleOpts(title="签名情感与性别分析"))
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}"))
        )
        return sun

    def analyseHeadImgIsHumanBySex(self):
        datas = self.df_friends.groupby(['Sex', 'IsHuman']).size()
        datas = datas.unstack()
        bar =(
            Bar().add_xaxis(datas.index.tolist())
            .add_yaxis("不使用人脸头像", datas['否'].values.tolist())
            .add_yaxis("使用人脸头像", datas['是'].values.tolist())
            .set_global_opts(
                title_opts=opts.TitleOpts(title="头像人像分析"),
                yaxis_opts=opts.AxisOpts(name="人数"),
                xaxis_opts=opts.AxisOpts(name="性别"),
            )
        )
        return bar

    def analyseHeadImgTags(self):
        datas = self.df_friends['HeadImgTags']
        dic = {}
        for data in datas.values:
            data = ast.literal_eval(data)
            for i in data:
                if i not in dic.keys():
                    dic[i] = 1
                else:
                    dic[i] += 1
        values = list(dic.items())
        pie = (
            Pie()
            .add(
                "",
                values,
                center=["40%", "50%"],
            ).set_global_opts(
                title_opts=opts.TitleOpts(title="头像种类占比"),
                legend_opts=opts.LegendOpts(
                    type_="scroll", pos_left="80%", orient="vertical"
                ),
            ).set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}，占{d}%"))
        )

        return pie

    def putEmotiomInSex(self,sex,dic,data):
        if sex=='男':
            dic[0]["children"].append(data)
        elif sex=='女':
            dic[1]["children"].append(data)
        elif sex=='未设置':
            dic[2]["children"].append(data)

    def createRandomColor(self):
        colorArr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
        color = ""
        for i in range(6):
            color += np.random.choice(colorArr)
        return '#'+color

    def analyseAll(self):
        a=self.analyseSex()
        b1,b2 = self.analyseGeo()
        c=self.analyseSignature()
        e=self.analyseHeadImgIsHumanBySex()
        f=self.analyseHeadImgTags()
        d = self.analyseSignatureEmotion()
        self.page.add(a).add(b1).add(b2).add(d).add(c).add(e).add(f)
        self.page.render(os.path.join('userdata',self.username,'result.html'))




def analyseAll(username):
    analyse=Analyse(username)
    analyse.analyseAll()


