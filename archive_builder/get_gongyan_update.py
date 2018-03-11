#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import requests
import re
import os
import shutil
from bs4 import BeautifulSoup
from datetime import datetime


def get_new_stream(sourcedate):

    # API='https://space.bilibili.com/ajax/member/getSubmitVideos?mid=22340288&pagesize=30&tid=0&page=1&keyword=&order=pubdate'
    API = 'https://space.bilibili.com/ajax/member/getSubmitVideos?mid=9247194&pagesize=30&tid=0&page=1&keyword=&order=pubdate'
    r = requests.get(API)
    json_content = r.json()

    vlist = json_content['data']['vlist']

    new_addition = []

    for video in vlist:
        title = video['title']
        aid = int(video['aid'])
        url = "https://www.bilibili.com/video/av" + str(aid)

        if "命运的X号" in title and "公演" in title:
            try:
                date = re.search(r'\d{8}',title).group(0)
            except:
                r2 = requests.get(url)
                soup = BeautifulSoup(r2.content, 'lxml')
                date = soup.find('meta', {'itemprop':'uploadDate'})['content']
                date = date[:4] + date[5:7] + date[8:10]

            title = date + " " + title.replace(date, '').strip()
            if datetime.strptime(date, '%Y%m%d') > datetime.strptime(sourcedate, '%Y%m%d'):
                new_addition.append({'title':title, 'url':url, 'aid':aid})

    return new_addition

def update_gongyan_archive():
    print("更新《命运的X号》公演cut")
    sourcefolder = os.path.abspath(os.path.join(os.getcwd(), "..")) + os.path.sep + "文章" + os.path.sep + "补档模块" + os.path.sep
    sourcefile = sourcefolder + "公演.txt"
    sourcestring = ""
    sourcedate = datetime.now().strftime('%Y%m%d')

    try:
        with codecs.open(sourcefile, 'r', encoding='utf-8') as f:
            lineno = 1
            for line in f:
                if codecs.BOM_UTF8.decode('utf-8') in line:
                    line = line.replace(codecs.BOM_UTF8.decode('utf-8'),"")
                if lineno == 5: # 最新记录的公演，目前为《命运的X号》
                    sourcedate = re.search(r'\d{8}', line).group(0)
                if lineno>4:
                    sourcestring += line

                lineno+=1
    except Exception as e:
        print(e)

    new_stream_items = get_new_stream(sourcedate)
    if new_stream_items:
        print("共更新%d条信息" % len(new_stream_items))
        with codecs.open(sourcefolder + "temp.txt",'w',encoding='utf-8') as f:
            result = ""
            for video in new_stream_items:
               result = result + video['title'] + os.linesep + video['url'] + os.linesep + os.linesep

            head_string = "公演" + os.linesep + os.linesep + "#《命运的X号》" + os.linesep + os.linesep
            result = head_string + result + sourcestring
            f.write(result)

        try:
            shutil.copy2(sourcefolder + 'temp.txt', sourcefolder + '公演.txt')
            os.remove(sourcefolder + 'temp.txt')
        except Exception as e:
            print(e)
    else:
        print("没有新信息")
