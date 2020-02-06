#!/usr/bin/env python
# coding: utf-8

# + 数据源 [腾讯疫情实时追踪](https://news.qq.com/zt2020/page/feiyan.htm?from=timeline&isappinstalled=0)

# ### 第一部分 网页分析

# ### 第二部分 数据准备

# #### 导入模块

import time
import json
import requests
from datetime import datetime
import pandas as pd
import numpy as np


# #### 抓取数据

def catch_data():
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5'
    reponse = requests.get(url=url).json()
    # 返回数据字典
    data = json.loads(reponse['data'])
    return data

data = catch_data()
data.keys()

# #### 数据处理

# 数据集包括["国内总量","国内新增","更新时间","数据明细","每日数据","每日新增"]

lastUpdateTime = data['lastUpdateTime']
chinaTotal = data['chinaTotal']
chinaAdd = data['chinaAdd']
print(chinaTotal)
print(chinaAdd)

# ##### 国内数据处理 第一步
# 数据明细，数据结构比较复杂，一步一步打印出来看，先明白数据结构
areaTree = data['areaTree']
# 国内数据
china_data = areaTree[0]['children']
china_list = []
for a in range(len(china_data)):
    province = china_data[a]['name']
    province_list = china_data[a]['children']
    for b in range(len(province_list)):
        city = province_list[b]['name']
        total = province_list[b]['total']
        today = province_list[b]['today']
        china_dict = {}
        china_dict['province'] = province
        china_dict['city'] = city
        china_dict['total'] = total
        china_dict['today'] = today
        china_list.append(china_dict)

china_data = pd.DataFrame(china_list)
china_data.head()


# ##### 国内数据处理 第二步

# 定义数据处理函数
def confirm(x):
    confirm = eval(str(x))['confirm']
    return confirm

def suspect(x):
    suspect = eval(str(x))['suspect']
    return suspect

def dead(x):
    dead = eval(str(x))['dead']
    return dead

def heal(x):
    heal = eval(str(x))['heal']
    return heal


# 函数映射
china_data['confirm'] = china_data['total'].map(confirm)
china_data['suspect'] = china_data['total'].map(suspect)
china_data['dead'] = china_data['total'].map(dead)
china_data['heal'] = china_data['total'].map(heal)
china_data['addconfirm'] = china_data['today'].map(confirm)
china_data['addsuspect'] = china_data['today'].map(suspect)
china_data['adddead'] = china_data['today'].map(dead)
china_data['addheal'] = china_data['today'].map(heal)
china_data = china_data[
    ["province", "city", "confirm", "suspect", "dead", "heal", "addconfirm", "addsuspect", "adddead", "addheal"]]
china_data.head()

# ##### 国际数据处理

global_data = pd.DataFrame(data['areaTree'])
global_data['confirm'] = global_data['total'].map(confirm)
global_data['suspect'] = global_data['total'].map(suspect)
global_data['dead'] = global_data['total'].map(dead)
global_data['heal'] = global_data['total'].map(heal)
global_data['addconfirm'] = global_data['today'].map(confirm)
global_data['addsuspect'] = global_data['today'].map(suspect)
global_data['adddead'] = global_data['today'].map(dead)
global_data['addheal'] = global_data['today'].map(heal)
world_name = pd.read_excel("世界各国中英文对照.xlsx")
global_data = pd.merge(global_data, world_name, left_on="name", right_on="中文", how="inner")
global_data = global_data[
    ["name", "英文", "confirm", "suspect", "dead", "heal", "addconfirm", "addsuspect", "adddead", "addheal"]]
global_data.head()

# ##### 日数据处理

chinaDayList = pd.DataFrame(data['chinaDayList'])
chinaDayList = chinaDayList[['date', 'confirm', 'suspect', 'dead', 'heal']]
chinaDayList.head()

# ##### 日新增数据处理


chinaDayAddList = pd.DataFrame(data['chinaDayAddList'])
chinaDayAddList = chinaDayAddList[['date', 'confirm', 'suspect', 'dead', 'heal']]
chinaDayAddList.head()

# ### 数据可视化

# #### 总数据明细
from pyecharts.charts import *  # 导入所有图表
from pyecharts import options as opts
# 导入pyecharts的主题（如果不使用可以跳过）
from pyecharts.globals import ThemeType

total_pie = Pie(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS, width='500px', height='350px'))  # 设置主题，和画布大小
total_pie.add("", [list(z) for z in zip(chinaTotal.keys(), chinaTotal.values())],
              center=["50%", "50%"],  # 图的位置
              radius=[50, 80])  # 内外径大小
total_pie.set_global_opts(
    title_opts=opts.TitleOpts(title="全国总量", subtitle=("截止" + lastUpdateTime)))
total_pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{c}"))  # 标签格式


totaladd_pie = Pie(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS, width='500px', height='350px'))  # 设置主题，和画布大小
totaladd_pie.add("", [list(z) for z in zip(chinaAdd.keys(), chinaAdd.values())],
                 center=["50%", "50%"],
                 radius=[50, 80])
totaladd_pie.set_global_opts(
    title_opts=opts.TitleOpts(title="昨日新增", subtitle=("截止" + lastUpdateTime)))
totaladd_pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{c}"))  # 标签格式

# #### 全球疫情热图
world_map = Map(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS))
world_map.add("", [list(z) for z in zip(list(global_data["英文"]), list(global_data["confirm"]))], "world",
              is_map_symbol_show=False)
world_map.set_global_opts(title_opts=opts.TitleOpts(title="2019-nCoV 世界疫情地图", subtitle=("截止" + lastUpdateTime)),
                          visualmap_opts=opts.VisualMapOpts(is_piecewise=True,
                                                            pieces=[
                                                                {"min": 101, "label": '>100'},  # 不指定 max，表示 max 为无限大
                                                                {"min": 10, "max": 100, "label": '10-100'},
                                                                {"min": 0, "max": 9, "label": '0-9'}]))
world_map.set_series_opts(label_opts=opts.LabelOpts(is_show=False))

# #### 中国疫情地图热图绘制

# 数据处理
area_data = china_data.groupby("province")["confirm"].sum().reset_index()
area_data.columns = ["province", "confirm"]

area_map = Map(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS))
area_map.add("", [list(z) for z in zip(list(area_data["province"]), list(area_data["confirm"]))], "china",
             is_map_symbol_show=False)
area_map.set_global_opts(title_opts=opts.TitleOpts(title="2019-nCoV 中国疫情地图", subtitle=("截止" + lastUpdateTime)),
                         visualmap_opts=opts.VisualMapOpts(is_piecewise=True,
                                                           pieces=[
                                                               {"min": 1001, "label": '>1000', "color": "#9C0A0D"},
                                                               # 不指定 max，表示 max 为无限大
                                                               {"min": 500, "max": 1000, "label": '500-1000',
                                                                "color": "#E64B47"},
                                                               {"min": 101, "max": 499, "label": '101-499',
                                                                "color": "#FE8664"},
                                                               {"min": 10, "max": 100, "label": '10-100',
                                                                "color": "#FFD2A0"},
                                                               {"min": 0, "max": 9, "label": '0-9',
                                                                "color": "#FFEFD7"}]))

# #### 绘制每日数据趋势

# ##### 每日累计数据趋势
line1 = Line(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS))
line1.add_xaxis(list(chinaDayList["date"]))
line1.add_yaxis("治愈", list(chinaDayList["heal"]), is_smooth=True)
line1.add_yaxis("死亡", list(chinaDayList["dead"]), is_smooth=True)
line1.set_global_opts(title_opts=opts.TitleOpts(title="治愈与死亡趋势", subtitle=("截止" + lastUpdateTime)))

line2 = Line(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS))
line2.add_xaxis(list(chinaDayList["date"]))
line2.add_yaxis("确诊", list(chinaDayList["confirm"]))
line2.add_yaxis("疑似", list(chinaDayList["suspect"]))
line2.set_global_opts(title_opts=opts.TitleOpts(title="确诊与疑似趋势", subtitle=("截止" + lastUpdateTime)))

bar = Bar(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS, width='900px', height='400px'))
bar.add_xaxis(list(chinaDayAddList["date"]))
bar.add_yaxis("确诊", list(chinaDayAddList["confirm"]))
bar.add_yaxis("疑似", list(chinaDayAddList["suspect"]))
bar.add_yaxis("死亡", list(chinaDayAddList["dead"]))
bar.add_yaxis("治愈", list(chinaDayAddList["heal"]))
bar.set_global_opts(title_opts=opts.TitleOpts(title="每日新增数据趋势", subtitle=("截止" + lastUpdateTime)))

# ### 图片汇总
page = Page()
page.add(total_pie)
page.add(totaladd_pie)
page.add(area_map)
page.add(world_map)
page.add(bar)
page.add(line2)
page.add(line1)
page.render("2019-nCoV.html")
