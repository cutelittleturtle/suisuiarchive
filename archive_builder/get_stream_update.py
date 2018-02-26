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

    API='https://space.bilibili.com/ajax/member/getSubmitVideos?mid=9247194&pagesize=30&tid=0&page=1&keyword=&order=pubdate'

    r = requests.get(API)
    json_content = r.json()

    vlist = json_content['data']['vlist']

    new_addition = []

    for video in vlist:
        title = video['title']
        aid = int(video['aid'])
        url = "https://www.bilibili.com/video/av" + str(aid)

        if "小学生日记" in title or "电台" in title:
            try:
                date = re.search(r'\d{6}',title).group(0)
                date = '20' + date[:2] + '-' + date[2:4] + '-' + date[4:6]
                title = re.search(r'.*\d{6}', title).group(0)[:-7]
            except:
                r2 = requests.get(url)
                soup = BeautifulSoup(r2.content, 'lxml')
                date = soup.find('time')['datetime'][:10]

            #print(date + " " + title, url)
            if datetime.strptime(date, '%Y-%m-%d') > datetime.strptime(sourcedate, '%Y-%m-%d'):
                new_addition.append({'title':date + " " + title, 'url':url, 'aid':aid})

    return new_addition

def update_stream_archive():
    print("更新直播-睡前半小时")
    sourcefolder = os.path.abspath(os.path.join(os.getcwd(), "..")) + os.path.sep + "文章" + os.path.sep + "直播模块" + os.path.sep
    sourcefile = sourcefolder + "睡前半小时.txt"
    sourcestring = ""
    sourcedate = datetime.now().strftime('%Y-%m-%d')

    try:
        with codecs.open(sourcefile, 'r', encoding='utf-8') as f:
            lineno = 1
            for line in f:
                if codecs.BOM_UTF8.decode('utf-8') in line:
                    line = line.replace(codecs.BOM_UTF8.decode('utf-8'),"")
                if lineno == 3:
                    sourcedate = line[:10]
                if lineno>2:
                    sourcestring += line

                lineno+=1
    except Exception as e:
        print(e)

    new_stream_items = get_new_stream(sourcedate)
    MODIFIED = False
    if new_stream_items:
        print("共更新%d条信息" % len(new_stream_items))
        with codecs.open(sourcefolder + "temp.txt",'w',encoding='utf-8') as f:
            result = '睡前半小时' + os.linesep + os.linesep
            for video in new_stream_items:
               result = result + video['title'] + os.linesep + video['url'] + os.linesep + os.linesep

            result = result + sourcestring
            f.write(result)

        try:
            shutil.copy2(sourcefolder + 'temp.txt', sourcefolder + '睡前半小时.txt')
            os.remove(sourcefolder + 'temp.txt')
            MODIFIED = True
        except Exception as e:
            print(e)
    else:
        print("没有新信息")

    filenames = [sourcefolder + "特殊.txt", sourcefolder + "睡前半小时.txt", sourcefolder + "小学生日记.txt", sourcefolder + "更多.txt"]
    if MODIFIED:
        try:
            with codecs.open(sourcefolder + '直播.txt', 'w', encoding='utf-8') as fo:
                for fname in filenames:
                    with codecs.open(fname, 'r', encoding='utf-8') as fi:
                        for line in fi:
                            if codecs.BOM_UTF8.decode('utf-8') in line:
                                line = line.replace(codecs.BOM_UTF8.decode('utf-8'),"")
                            fo.write(line)
                        fo.write(os.linesep + os.linesep)

            shutil.copy2(sourcefolder + '直播.txt', os.path.abspath(os.path.join(sourcefolder, "..")) + os.path.sep + '直播.txt')
            os.remove(sourcefolder + '直播.txt')

        except Exception as e:
            print(e)