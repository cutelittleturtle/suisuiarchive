#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import requests
import re
import os
import shutil
from bs4 import BeautifulSoup
from datetime import datetime
import sys


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

    return text

def get_sourcedate():

    timefile = os.path.abspath(os.path.join(os.getcwd(), "..")) + os.path.sep + "文章" + os.path.sep + "更新时间.txt"
    sourcedate_gongyan = ""
    sourcedate_stream = ""
    sourcedate_waiwu = ""
    sourcedate_unattended = ""

    with codecs.open(timefile, 'r', encoding='utf-8') as f:
        for line in f:
            if "公演" in line:
                sourcedate_gongyan = line.split(',')[-1].strip()
            if "直播" in line:
                sourcedate_stream = line.split(',')[-1].strip()
            if "外务" in line:
                sourcedate_waiwu = line.split(',')[-1].strip()
            if "其它" in line:
                sourcedate_unattended = line.split(',')[-1].strip()

    return {"gongyan": sourcedate_gongyan, "stream": sourcedate_stream, "waiwu": sourcedate_waiwu, "unattended": sourcedate_unattended}

def update_sourcedate(u_dates):
    timefile_dir = os.path.abspath(os.path.join(os.getcwd(), "..")) + os.path.sep + "文章" + os.path.sep

    sourcedate_gongyan, sourcedate_stream, sourcedate_waiwu, sourcedate_unattended = u_dates

    with codecs.open(timefile_dir + "temp.txt", 'w', encoding='utf-8') as f:
        f.write(("公演, %s" % sourcedate_gongyan) + os.linesep)
        f.write(("直播, %s" % sourcedate_stream) + os.linesep)
        f.write(("外务, %s" % sourcedate_waiwu) + os.linesep)
        f.write(("其它, %s" % sourcedate_unattended) + os.linesep)

    shutil.copy2(timefile_dir + 'temp.txt', timefile_dir + "更新时间.txt")
    os.remove(timefile_dir + 'temp.txt')

def get_date_from_title(title, url, slash=False):

    format_slash = "%s-%s-%s"
    format_normal = "%s%s%s"

    found = re.search(r'\d{8}',title)
    if found: # 20170212
        date = found.group(0)
        Y = date[:4]
        m = date[4:6]
        d = date[6:8]
    else: # 170212
        found = re.search(r'\d{6}',title)
        if found:
            date = found.group(0)
            Y = '20' + date[:2]
            m = date[2:4]
            d = date[4:6]
        else: # no date in title
            r2 = requests.get(url)
            soup = BeautifulSoup(r2.content, 'lxml')
            date = soup.find('meta', {'itemprop':'uploadDate'})['content'][:10]
            Y = date[:4]
            m = date[5:7]
            d = date[8:10]

    date = format_slash % (Y,m,d) if slash else format_normal % (Y,m,d)

    return date

def writedisk_gongyan(new_gongyan, FORCE=False):
    '''
    '''
    gongyan_title = "《命运的X号》"

    print("更新%s公演cut" % gongyan_title)

    if new_gongyan or FORCE:
        print("共更新%d条信息" % len(new_gongyan))

        sourcefolder = os.path.abspath(os.path.join(os.getcwd(), "..")) + os.path.sep + "文章" + os.path.sep + "补档模块" + os.path.sep
        sourcefile = sourcefolder + "公演.txt"

        sourcestring = ""
        try:
            with codecs.open(sourcefile, 'r', encoding='utf-8') as f:
                lineno = 1
                for line in f:
                    if codecs.BOM_UTF8.decode('utf-8') in line:
                        line = line.replace(codecs.BOM_UTF8.decode('utf-8'),"")
                    if lineno>4:
                        sourcestring += line
                    lineno+=1
        except Exception as e:
            print(e)

        with codecs.open(sourcefolder + "temp.txt",'w',encoding='utf-8') as f:
            result = ""
            for video in new_gongyan:
               result = result + video['title'] + os.linesep + video['url'] + os.linesep + os.linesep

            head_string = "公演" + os.linesep + os.linesep + "#%s" % gongyan_title + os.linesep + os.linesep
            result = head_string + result + sourcestring
            f.write(result)

        try:
            shutil.copy2(sourcefolder + 'temp.txt', sourcefolder + '公演.txt')
            os.remove(sourcefolder + 'temp.txt')
        except Exception as e:
            print(e)
    else:
        print("没有新信息" + os.linesep)

def writedisk_stream(new_stream, FORCE=False):
    '''
    '''
    stream_title = "睡前半小时"
    print("更新直播-%s" % stream_title)

    MODIFIED = False
    if new_stream or FORCE:
        print("共更新%d条信息" % len(new_stream))
        MODIFIED = False

        sourcefolder = os.path.abspath(os.path.join(os.getcwd(), "..")) + os.path.sep + "文章" + os.path.sep + "直播模块" + os.path.sep
        sourcefile = sourcefolder + ("%s.txt" % stream_title)
        sourcestring = ""

        # get existing info
        try:
            with codecs.open(sourcefile, 'r', encoding='utf-8') as f:
                lineno = 1
                for line in f:
                    if codecs.BOM_UTF8.decode('utf-8') in line:
                        line = line.replace(codecs.BOM_UTF8.decode('utf-8'),"")
                    if lineno>2:
                        sourcestring += line
                    lineno+=1
        except Exception as e:
            print(e)

        # write temp file with updated info
        with codecs.open(sourcefolder + "temp.txt",'w',encoding='utf-8') as f:
            result = ('%s' % stream_title) + os.linesep + os.linesep
            for video in new_stream:
               result = result + video['title'] + os.linesep + video['url'] + os.linesep + os.linesep

            result = result + sourcestring
            f.write(result)

        # temp > title
        try:
            shutil.copy2(sourcefolder + 'temp.txt', sourcefolder + ('%s.txt' % stream_title))
            os.remove(sourcefolder + 'temp.txt')
            MODIFIED = True
        except Exception as e:
            print(e)

        # concatenate
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

    else:
        print("没有新信息" + os.linesep)

def writedisk_waiwu(new_waiwu, FORCE=False):
    '''
    '''
    waiwu_title = "48狼人杀"
    print("更新外务-%s" % waiwu_title)

    if new_waiwu or FORCE:
        print("共更新%d条信息" % len(new_waiwu))

        sourcefolder = os.path.abspath(os.path.join(os.getcwd(), "..")) + os.path.sep + "文章" + os.path.sep + "外务模块" + os.path.sep
        sourcefile = sourcefolder + ("%s.txt" % waiwu_title)
        sourcestring = ""

        try:
            with codecs.open(sourcefile, 'r', encoding='utf-8') as f:
                lineno = 1
                for line in f:
                    if codecs.BOM_UTF8.decode('utf-8') in line:
                        line = line.replace(codecs.BOM_UTF8.decode('utf-8'),"")
                    if lineno>2:
                        sourcestring += line
                    lineno+=1
        except Exception as e:
            print(e)

        MODIFIED = False

        with codecs.open(sourcefolder + "temp.txt",'w',encoding='utf-8') as f:
            result = ('#《%s》' % waiwu_title) + os.linesep + os.linesep
            for video in new_waiwu:
               result = result + video['title'] + os.linesep + video['url'] + os.linesep + os.linesep

            result = result + sourcestring
            f.write(result)

        try:
            shutil.copy2(sourcefolder + 'temp.txt', sourcefolder + ('%s.txt' % waiwu_title))
            os.remove(sourcefolder + 'temp.txt')
            MODIFIED = True
        except Exception as e:
            print(e)

        filenames = [sourcefolder + "外务.txt", sourcefolder + "团内活动.txt", sourcefolder + "48狼人杀.txt", sourcefolder + "演唱会.txt",
                    sourcefolder + "2016.txt", sourcefolder + "2015.txt", sourcefolder + "国民美少女.txt", sourcefolder + "星APP风云榜.txt",
                    sourcefolder + "塞纳河畔夜谈.txt"]

        if MODIFIED:
            try:
                with codecs.open(sourcefolder + '最新活动.txt', 'w', encoding='utf-8') as fo:
                    for fname in filenames:
                        with codecs.open(fname, 'r', encoding='utf-8') as fi:
                            for line in fi:
                                if codecs.BOM_UTF8.decode('utf-8') in line:
                                    line = line.replace(codecs.BOM_UTF8.decode('utf-8'),"")
                                fo.write(line)
                            fo.write(os.linesep + os.linesep)

                shutil.copy2(sourcefolder + '最新活动.txt',
                        os.path.abspath(os.path.join(sourcefolder, "..")) + os.path.sep + '补档模块' + os.path.sep + '最新活动.txt')
                os.remove(sourcefolder + '最新活动.txt')
            except Exception as e:
                print(e)
    else:
        print("没有新信息" + os.linesep)

def writedisk_unattended(new_unattended, FORCE=False):
    '''
    '''
    print("更新 未整理")

    if new_unattended or FORCE:
        print("共更新%d条信息" % len(new_unattended))
        sourcefolder = os.path.abspath(os.path.join(os.getcwd(), "..")) + os.path.sep + "文章" + os.path.sep
        sourcefile = sourcefolder + "未整理.txt"
        sourcestring = ""

        try:
            with codecs.open(sourcefile, 'r', encoding='utf-8') as f:
                lineno = 1
                for line in f:
                    if codecs.BOM_UTF8.decode('utf-8') in line:
                        line = line.replace(codecs.BOM_UTF8.decode('utf-8'),"")
                    sourcestring += line
                    lineno+=1
        except Exception as e:
            print(e)

        with codecs.open(sourcefolder + "temp.txt",'w',encoding='utf-8') as f:
            result = ""
            for video in new_unattended:
               result = result + video['title'] + os.linesep + video['url'] + os.linesep + os.linesep

            result = result + sourcestring
            f.write(result)

        try:
            shutil.copy2(sourcefolder + 'temp.txt', sourcefolder + '未整理.txt')
            os.remove(sourcefolder + 'temp.txt')
            shutil.copy2(sourcefolder + '未整理.txt', os.path.abspath(os.path.join(os.getcwd(), "..")) + os.path.sep
                    + "app" + os.path.sep + "assets")
        except Exception as e:
            print(e)
    else:
        print("没有新信息" + os.linesep)

def retrieve_feeds():
    ''' read new updated video on 杨冰怡应援会, dispatch them to sections
        return [gongyan, stream, waiwu, unattended]
    '''
    API = 'https://space.bilibili.com/ajax/member/getSubmitVideos?mid=9247194&pagesize=30&tid=0&page=1&keyword=&order=pubdate'

    r = requests.get(API)
    json_content = r.json()

    vlist = json_content['data']['vlist']

    gongyan = [] # 公演, 命运的X
    stream = [] # 直播
    waiwu = [] # 外务 - 狼人杀
    unattended = [] # 未分类

    sourcedate_gongyan, sourcedate_stream, sourcedate_waiwu, sourcedate_unattended = list(get_sourcedate().values())

    u_sourcedate_gongyan = sourcedate_gongyan
    u_sourcedate_stream = sourcedate_stream
    u_sourcedate_waiwu = sourcedate_waiwu
    u_sourcedate_unattended = sourcedate_unattended

    for video in vlist:
        title = remove_nbws(video['title']).strip()
        aid = int(video['aid'])
        url = "https://www.bilibili.com/video/av" + str(aid)

        if "命运的X号" in title:
            sourcedate = sourcedate_gongyan if sourcedate_gongyan else datetime.now().strftime('%Y%m%d')
            date = get_date_from_title(title, url, slash=False)
            title = date + " " + title.replace(date, '').strip()

            if datetime.strptime(date, '%Y%m%d') > datetime.strptime(sourcedate, '%Y%m%d'):
                print(title)
                gongyan.append({'title':title, 'url':url, 'aid':aid})
                if datetime.strptime(date, '%Y%m%d') > datetime.strptime(u_sourcedate_gongyan, '%Y%m%d'):
                    u_sourcedate_gongyan = date

        elif "小学生日记" in title or "电台" in title:
            sourcedate = sourcedate_stream if sourcedate_stream else datetime.now().strftime('%Y-%m-%d')
            date = get_date_from_title(title, url, slash=True)
            title = date + " " + title.replace('【SNH48】', '').replace('【杨冰怡】', '')

            if datetime.strptime(date, '%Y-%m-%d') > datetime.strptime(sourcedate, '%Y-%m-%d'):
                print(title)
                stream.append({'title':title, 'url':url, 'aid':aid})
                if datetime.strptime(date, '%Y-%m-%d') > datetime.strptime(u_sourcedate_stream, '%Y-%m-%d'):
                    u_sourcedate_stream = date

        elif "狼人杀" in title:
            sourcedate = sourcedate_waiwu if sourcedate_waiwu else datetime.now().strftime('%Y%m%d')
            date = get_date_from_title(title, url, slash=False)
            title = date + " " + title.replace(date, '').strip()

            if datetime.strptime(date, '%Y%m%d') > datetime.strptime(sourcedate, '%Y%m%d'):
                print(title)
                waiwu.append({'title':title, 'url':url, 'aid':aid})
                if datetime.strptime(date, '%Y%m%d') > datetime.strptime(u_sourcedate_waiwu, '%Y%m%d'):
                    u_sourcedate_waiwu = date

        else:
            sourcedate = sourcedate_unattended if sourcedate_unattended else datetime.now().strftime('%Y-%m-%d')
            date = get_date_from_title(title, url, slash=True)
            title = date + " " + title

            if datetime.strptime(date, '%Y-%m-%d') > datetime.strptime(sourcedate, '%Y-%m-%d'):
                print("unattended: " + title)
                unattended.append({'title':title, 'url':url, 'aid':aid})
                u_sourcedate_unattended = date

    return [gongyan, stream, waiwu, unattended, [u_sourcedate_gongyan, u_sourcedate_stream, u_sourcedate_waiwu, u_sourcedate_unattended]]

def update_archive():
    ''' wrapper main function
    '''
    try:
        gongyan, stream, waiwu, unattended, u_dates = retrieve_feeds()

        # enable file rewriting to update any manual changes
        writedisk_gongyan(gongyan, FORCE=True)
        writedisk_stream(stream, FORCE=True)
        writedisk_waiwu(waiwu, FORCE=True)
        writedisk_unattended(unattended, FORCE=True)

        if u_dates:
            update_sourcedate(u_dates)
    except Exception as e:
        print(e)
        sys.exit()

def main():
    update_archive()

if __name__ == "__main__":
    main()


