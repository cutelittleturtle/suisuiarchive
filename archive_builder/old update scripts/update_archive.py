#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import requests
import re
import os
import shutil
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
import sys
import logging

API = 'https://space.bilibili.com/ajax/member/getSubmitVideos?mid=9247194&pagesize=30&tid=0&page=1&keyword=&order=pubdate'

script_dir = os.getcwd()
root_dir = os.path.abspath(os.path.join(script_dir, ".."))
archive_dir = os.path.abspath(os.path.join(os.getcwd(), "..")) + os.path.sep + "文章"

fn_lastupdated = "更新时间.txt"
gongyan_title = "《命运的X号》"
stream_title = "睡前半小时"
waiwu_title = "48狼人杀"


dateformat_gongyan = '%Y%m%d'
dateformat_stream = '%Y-%m-%d'
dateformat_waiwu = '%Y%m%d'
dateformat_unattended = '%Y-%m-%d'

ext_msg1 = "Exit without finish."

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
    ''' get last updated date for components
    '''
    logger = logging.getLogger()

    sourcedate_file = archive_dir + os.path.sep + fn_lastupdated
    sourcedate_gongyan = ""
    sourcedate_stream = ""
    sourcedate_waiwu = ""
    sourcedate_unattended = ""

    if not os.path.isfile(sourcedate_file):
        update_sourcedate([], create=True)

    try:
        with codecs.open(sourcedate_file, 'r', encoding='utf-8') as f:
            for line in f:
                if "公演" in line:
                    sourcedate_gongyan = line.split(',')[-1].strip()
                if "直播" in line:
                    sourcedate_stream = line.split(',')[-1].strip()
                if "外务" in line:
                    sourcedate_waiwu = line.split(',')[-1].strip()
                if "其它" in line:
                    sourcedate_unattended = line.split(',')[-1].strip()
    except Exception as e:
        logger.exception("File reading error on: %s." % fn_lastupdated)
        logger.error(e)
        sys.exit(ext_msg1)

    return {"gongyan": sourcedate_gongyan, "stream": sourcedate_stream, "waiwu": sourcedate_waiwu, "unattended": sourcedate_unattended}

def update_sourcedate(u_dates, create=False):
    ''' update "更新时间.txt" with new entries
        or create new one based on yesterday's date
    '''
    logger = logging.getLogger()

    if u_dates:
        sourcedate_gongyan, sourcedate_stream, sourcedate_waiwu, sourcedate_unattended = u_dates
    elif create:
        yesterday = date.today() - timedelta(1)
        sourcedate_gongyan = yesterday.strftime(dateformat_gongyan)
        sourcedate_stream = yesterday.strftime(dateformat_stream)
        sourcedate_waiwu = yesterday.strftime(dateformat_waiwu)
        sourcedate_unattended = yesterday.strftime(dateformat_unattended)
    else:
        logger.error("Error updating 更新时间.txt::no valid input dates, nor allow creating new one")

        sys.exit(ext_msg1)

    try:
        with codecs.open(archive_dir + os.path.sep + "temp.txt", 'w', encoding='utf-8') as f:
            f.write(("公演, %s" % sourcedate_gongyan) + os.linesep)
            f.write(("直播, %s" % sourcedate_stream) + os.linesep)
            f.write(("外务, %s" % sourcedate_waiwu) + os.linesep)
            f.write(("其它, %s" % sourcedate_unattended) + os.linesep)

        shutil.copy2(archive_dir + os.path.sep + 'temp.txt', archive_dir + os.path.sep + "更新时间.txt")
        os.remove(archive_dir + os.path.sep + 'temp.txt')
    except Exception as e:
        logger.exception("File operation error: update_sourcedate::update 更新时间.txt")
        logger.error(e)
        sys.exit(ext_msg1)

def get_date_from_title(title, url, slash=False):
    ''' translate bilibili time to string time. If not possible, get the publish date from url.
    '''

    def get_url_date(url):
        try:
            r2 = requests.get(url)
            soup = BeautifulSoup(r2.content, 'lxml')
            date = soup.find('meta', {'itemprop':'uploadDate'})['content'][:10]
            Y = date[:4]
            m = date[5:7]
            d = date[8:10]
            return [Y, m, d]
        except Exception as e:
            logger.error("Error getting publish time from: %s" % url)
            logger.error(e)
            sys.exit(ext_msg1)

    logger = logging.getLogger()

    format_slash = "%s-%s-%s"
    format_normal = "%s%s%s"

    found = re.search(r'\d{8}',title)
    if found: # 20170212
        date = found.group(0)
        Y = date[:4]
        m = date[4:6]
        d = date[6:8]
    elif re.search(r'\d{6}',title): # 170212
        found = re.search(r'\d{6}',title)
        if found:
            date = found.group(0)
            Y = '20' + date[:2]
            m = date[2:4]
            d = date[4:6]
    else:
        Y, m, d = get_url_date(url)

    date = format_slash % (Y,m,d) if slash else format_normal % (Y,m,d)

    try:
        tester = datetime.strptime(date, "%Y-%m-%d") if slash else datetime.strptime(date, "%Y%m%d")
    except:
        Y, m, d = get_url_date(url)
        date = format_slash % (Y,m,d) if slash else format_normal % (Y,m,d)

    return date

def writedisk_gongyan(new_gongyan, FORCE=False):
    ''' write gongyan to gongyan file
    '''
    global gongyan_title
    logger = logging.getLogger()

    logger.info("更新%s公演cut" % gongyan_title)

    if new_gongyan or FORCE:
        logger.info("共更新%d条信息" % len(new_gongyan))

        sourcefolder = root_dir + os.path.sep + "文章" + os.path.sep + "补档模块" + os.path.sep
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

            with codecs.open(sourcefolder + "temp.txt",'w',encoding='utf-8') as fw:
                result = ""
                for video in new_gongyan:
                  result = result + video['title'] + os.linesep + video['url'] + os.linesep + os.linesep

                head_string = "公演" + os.linesep + os.linesep + "#%s" % gongyan_title + os.linesep + os.linesep
                result = head_string + result + sourcestring
                fw.write(result)

            shutil.copy2(sourcefolder + 'temp.txt', sourcefolder + '公演.txt')
            #os.remove(sourcefolder + 'temp.txt')

        except Exception as e:
            logger.exception("File operation error: writedisk_gongyan::%s" % "公演.txt")
            logger.error(e)
            sys.exit(ext_msg1)
    else:
        logger.info("没有新信息" + os.linesep)

def writedisk_stream(new_stream, FORCE=False):
    ''' write stream to stream file
    '''
    global stream_title
    logger = logging.getLogger()

    logger.info("更新直播-%s" % stream_title)
    MODIFIED = False

    if new_stream or FORCE:
        logger.info("共更新%d条信息" % len(new_stream))
        MODIFIED = False

        sourcefolder = root_dir + os.path.sep + "文章" + os.path.sep + "直播模块" + os.path.sep
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

            with codecs.open(sourcefolder + "temp.txt",'w',encoding='utf-8') as fw:
                result = ('%s' % stream_title) + os.linesep + os.linesep
                for video in new_stream:
                  result = result + video['title'] + os.linesep + video['url'] + os.linesep + os.linesep

                result = result + sourcestring
                fw.write(result)

            shutil.copy2(sourcefolder + 'temp.txt', sourcefolder + ('%s.txt' % stream_title))
            os.remove(sourcefolder + 'temp.txt')
            MODIFIED = True
        except Exception as e:
            logger.exception("File operation error: writedisk_stream::%s.txt" % stream_title)
            logger.error(e)
            sys.exit(ext_msg1)

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
                logger.exception("File concatenation error: writedisk_stream::%s" % "直播.txt")
                logger.error(e)
                sys.exit(ext_msg1)
    else:
        logger.info("没有新信息" + os.linesep)

def writedisk_waiwu(new_waiwu, FORCE=False):
    ''' write waiwu to waiwu file
    '''
    global waiwu_title
    logger = logging.getLogger()
    MODIFIED = False

    logger.info("更新外务-%s" % waiwu_title)

    if new_waiwu or FORCE:
        logger.info("共更新%d条信息" % len(new_waiwu))
        sourcefolder = root_dir + os.path.sep + "文章" + os.path.sep + "外务模块" + os.path.sep
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

            with codecs.open(sourcefolder + "temp.txt",'w',encoding='utf-8') as fw:
                result = ('#《%s》' % waiwu_title) + os.linesep + os.linesep
                for video in new_waiwu:
                  result = result + video['title'] + os.linesep + video['url'] + os.linesep + os.linesep
                result = result + sourcestring
                fw.write(result)

            shutil.copy2(sourcefolder + 'temp.txt', sourcefolder + ('%s.txt' % waiwu_title))
            os.remove(sourcefolder + 'temp.txt')
            MODIFIED = True
        except Exception as e:
            logger.exception("File operation error: writedisk_waiwu::%s.txt" % waiwu_title)
            logger.error(e)
            sys.exit(ext_msg1)

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
                logger.exception("File concatenation error: writedisk_waiwu::%s" % "最新活动.txt")
                logger.error(e)
                sys.exit(ext_msg1)
    else:
        logger.info("没有新信息" + os.linesep)

def writedisk_unattended(new_unattended, FORCE=False):
    ''' write unattended to unattended file
    '''
    logger = logging.getLogger()
    logger.info("更新 未整理")

    if new_unattended or FORCE:
        logger.info("共更新%d条信息" % len(new_unattended))
        sourcefolder = root_dir + os.path.sep + "文章" + os.path.sep
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

            with codecs.open(sourcefolder + "temp.txt",'w',encoding='utf-8') as fw:
                result = ""
                for video in new_unattended:
                  result = result + video['title'] + os.linesep + video['url'] + os.linesep + os.linesep

                result = result + sourcestring
                fw.write(result)

            shutil.copy2(sourcefolder + 'temp.txt', sourcefolder + '未整理.txt')
            os.remove(sourcefolder + 'temp.txt')
            shutil.copy2(sourcefolder + '未整理.txt', os.path.abspath(os.path.join(os.getcwd(), "..")) + os.path.sep
                    + "app" + os.path.sep + "assets")
        except Exception as e:
            logger.exception("File operation error: writedisk_waiwu::%s" % "未整理.txt")
            logger.error(e)
            sys.exit(ext_msg1)
    else:
        logger.info("没有新信息" + os.linesep)

def retrieve_feeds():
    ''' read new updated video on 杨冰怡应援会, dispatch them to sections
        return [gongyan, stream, waiwu, unattended]
    '''
    logger = logging.getLogger()
    global API

    try:
        r = requests.get(API)
        json_content = r.json()
    except Exception as e:
        logger.exception(e)
        sys.exit(ext_msg1)

    try:
        vlist = json_content['data']['vlist']
    except Exception as e:
        logger.error("Error getting vlist from %s" % API)
        sys.exit(ext_msg1)

    gongyan = [] # 公演, 命运的X
    stream = [] # 直播
    waiwu = [] # 外务 - 狼人杀
    unattended = [] # 未分类

    sourcedate_gongyan, sourcedate_stream, sourcedate_waiwu, sourcedate_unattended = list(get_sourcedate().values())

    u_sourcedate_gongyan = sourcedate_gongyan
    u_sourcedate_stream = sourcedate_stream
    u_sourcedate_waiwu = sourcedate_waiwu
    u_sourcedate_unattended = sourcedate_unattended

    print()
    logger.info("Last 公演 updated on: %s" % u_sourcedate_gongyan)
    logger.info("Last 直播 updated on: %s" % u_sourcedate_stream)
    logger.info("Last 外务 updated on: %s" % u_sourcedate_waiwu)
    logger.info("Last 未分类 updated on: %s" % u_sourcedate_unattended)
    print()

    for video in vlist:
        try:
            title = remove_nbws(video['title']).strip()
            aid = int(video['aid'])
            url = "https://www.bilibili.com/video/av" + str(aid)
            logger.info("Receiving feed: %s" % title)
        except Exception as e:
            logger.warn("Error decoding video[\'title\'] or [\'aid\']: %s" % video)
            logger.info("continue to next feed")
            continue

        if "公演" in title or gongyan_title in title:
            date = get_date_from_title(title, url, slash=False)
            title = date + " " + title.replace(date, '').strip()

            if datetime.strptime(date, dateformat_gongyan) > datetime.strptime(sourcedate_gongyan, dateformat_gongyan):
                gongyan.append({'title':title, 'url':url, 'aid':aid})
                if datetime.strptime(date, dateformat_gongyan) > datetime.strptime(u_sourcedate_gongyan, dateformat_gongyan):
                    u_sourcedate_gongyan = date

        elif "小学生日记" in title or "电台" in title or stream_title in title:
            date = get_date_from_title(title, url, slash=True)
            title = date + " " + title.replace('【SNH48】', '').replace('【杨冰怡】', '')

            if datetime.strptime(date, dateformat_stream) > datetime.strptime(sourcedate_stream, dateformat_stream):
                stream.append({'title':title, 'url':url, 'aid':aid})
                if datetime.strptime(date, dateformat_stream) > datetime.strptime(u_sourcedate_stream, dateformat_stream):
                    u_sourcedate_stream = date

        elif "狼人杀" in title or waiwu_title in title:
            date = get_date_from_title(title, url, slash=False)
            title = date + " " + title.replace(date, '').strip()

            if datetime.strptime(date, dateformat_waiwu) > datetime.strptime(sourcedate_waiwu, dateformat_waiwu):
                waiwu.append({'title':title, 'url':url, 'aid':aid})
                if datetime.strptime(date, dateformat_waiwu) > datetime.strptime(u_sourcedate_waiwu, dateformat_waiwu):
                    u_sourcedate_waiwu = date

        else:
            date = get_date_from_title(title, url, slash=True)
            title = date + " " + title

            if datetime.strptime(date, dateformat_unattended) > datetime.strptime(sourcedate_unattended, dateformat_unattended):
                unattended.append({'title':title, 'url':url, 'aid':aid})
                u_sourcedate_unattended = date

    return [gongyan, stream, waiwu, unattended, [u_sourcedate_gongyan, u_sourcedate_stream, u_sourcedate_waiwu, u_sourcedate_unattended]]

def update_archive():
    ''' wrapper main
    '''
    declare_logger()
    logger = logging.getLogger()

    gongyan, stream, waiwu, unattended, u_dates = retrieve_feeds()

    # enable file rewriting to update any manual changes
    writedisk_gongyan(gongyan, FORCE=True)
    writedisk_stream(stream, FORCE=True)
    writedisk_waiwu(waiwu, FORCE=True)
    writedisk_unattended(unattended, FORCE=True)

    if u_dates:
        update_sourcedate(u_dates)

def main():
    update_archive()

def declare_logger():
    logging.basicConfig(filename="log.txt", level=logging.DEBUG, format="%(message)s", filemode="w")
    logger = logging.getLogger()

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch_formatter = logging.Formatter("%(message)s")
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)


if __name__ == "__main__":
    main()


