#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import requests
import re
import os
import shutil
from bs4 import BeautifulSoup
from datetime import datetime

def remove_nbws(text):
    """ remove unwanted unicode punctuation: zwsp, nbws, \t, \r, \r.
    """

    # ZWSP: Zero width space
    text = text.replace(u'\u200B', '')
    # NBWS: Non-breaking space
    text = text.replace(u'\xa0', ' ')
    # HalfWidth fullstop
    text = text.replace(u'\uff61', '')
    # Bullet
    text = text.replace(u'\u2022', '')
    # White space
    text = text.replace(u'\t', ' ').replace(u'\r', ' ')

    # General Punctuation
    gpc_pattern = re.compile(r'[\u2000-\u206F]')
    text = gpc_pattern.sub('', text)

    # Mathematical Operator
    mop_pattern = re.compile(r'[\u2200-\u22FF]')
    text = mop_pattern.sub('', text)

    # Combining Diacritical Marks
    dcm_pattern = re.compile(r'[\u0300-\u036F]')
    text = dcm_pattern.sub('', text)

    lsp_pattern = re.compile(r'[\x80-\xFF]')
    text = lsp_pattern.sub('', text)

    text = re.sub(r'\s+', ' ', text)

    text = re.sub(r'\u00E1', '', text)

    return text

def get_unattended(sourcedate):

    API = 'https://space.bilibili.com/ajax/member/getSubmitVideos?mid=9247194&pagesize=30&tid=0&page=1&keyword=&order=pubdate'

    r = requests.get(API)
    json_content = r.json()

    vlist = json_content['data']['vlist']

    unattended = []

    for video in vlist:
        title = remove_nbws(video['title'])
        aid = int(video['aid'])
        url = "https://www.bilibili.com/video/av" + str(aid)

        if (not "小学生日记" in title) and (not "电台" in title) and (not ("命运的X号" in title and "公演" in title)):
            found = re.search(r'\d{8}',title)
            if found:
                date = found.group(0)
                date = date[:4] + '-' + date[4:6] + '-' + date[6:8]
            else:
                found = re.search(r'\d{6}',title)
                if found:
                    date = found.group(0)
                    date = '20' + date[:2] + '-' + date[2:4] + '-' + date[4:6]
                else:
                    r2 = requests.get(url)
                    soup = BeautifulSoup(r2.content, 'lxml')
                    date = soup.find('meta', {'itemprop':'uploadDate'})['content'][:10]

            if datetime.strptime(date, '%Y-%m-%d') > datetime.strptime(sourcedate, '%Y-%m-%d'):
                unattended.append({'title': date + " " + title, 'url':url, 'date': date})

    return unattended

def update_unattended_archive():
    print("更新 未整理")
    sourcefolder = os.path.abspath(os.path.join(os.getcwd(), "..")) + os.path.sep + "文章" + os.path.sep
    sourcefile = sourcefolder + "未整理.txt"
    sourcestring = ""
    sourcedate = datetime.now().strftime('%Y-%m-%d')

    try:
        with codecs.open(sourcefile, 'r', encoding='utf-8') as f:
            lineno = 1
            for line in f:
                if codecs.BOM_UTF8.decode('utf-8') in line:
                    line = line.replace(codecs.BOM_UTF8.decode('utf-8'),"")
                if lineno == 1:
                    sourcedate = line[:10]
                sourcestring += line
                lineno+=1
    except Exception as e:
        print(e)

    new_unattended_items = get_unattended(sourcedate)
    if new_unattended_items:
        print("共更新%d条信息" % len(new_unattended_items))
        with codecs.open(sourcefolder + "temp.txt",'w',encoding='utf-8') as f:
            result = ""
            for video in new_unattended_items:
               result = result + video['title'] + os.linesep + video['url'] + os.linesep + os.linesep

            result = result + sourcestring
            f.write(result)

        try:
            shutil.copy2(sourcefolder + 'temp.txt', sourcefolder + '未整理.txt')
            os.remove(sourcefolder + 'temp.txt')
            MODIFIED = True

            shutil.copy2(sourcefolder + '未整理.txt', os.path.abspath(os.path.join(os.getcwd(), "..")) + os.path.sep
                    + "app" + os.path.sep + "assets")

        except Exception as e:
            print(e)
    else:
        print("没有新信息")