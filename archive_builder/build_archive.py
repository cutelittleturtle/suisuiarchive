#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import os
import shutil

# This script read a text+url text file to produce a jekyll friendly post file for publihsing html

def _isurl(line):

    _urldef = ('http','https','www','ftp')
    if any(x in line for x in _urldef):
        return True
    else:
        return False

def build_archive_list(inputfile):
    """ create archive list.

    """
    archive = ""
    archive = archive + "{% block pageContent %}\n"
    with codecs.open(inputfile,'r',encoding="utf-8") as f:
        print('Opening file: ' + inputfile)
        firstsection = True
        header_count = 1

        pre_indentation = 2
        for line in f:
            outline2 = ""

            # remove UTF-BOM made by Windows notepad
            if codecs.BOM_UTF8.decode('utf-8') in line:
                line = line.replace(codecs.BOM_UTF8.decode('utf-8'),"")

            if "asset_img" in line:
                continue
            elif line.strip(): # start with non-empty lines
                try:
                    neline = next(f)
                except StopIteration: # if no next line, we have either empty header or useless info
                    print("End of file")
                    break

                if not neline.strip(): # if empty next line -> section header
                    sublist = True if line[0] == "#" else False
                    indentation = 4 if sublist else 2
                    line = line[1:].strip() if sublist else line.strip()

                    # check for bold markdown ** **
                    if line[0] == "*":
                        line = line[2:-2]


                    if not firstsection:
                        outline2 = outline2 + pre_indentation * " " + "</section>\n\n"

                    outline2 = outline2 + " " * indentation + "<section data-folding=\"" + line + "\">\n"
                    outline2 = (outline2 + " " * (indentation + 2) + ("<h3" if sublist else "<h2 class=\"page-header\"")
                                + " id=\"archive-header-" + str(header_count) + "\">"
                                + line + ("</h3>\n" if sublist else "</h2>\n"))
                    _id = 1
                    header_count += 1
                    pre_indentation = indentation
                    firstsection = False

                elif _isurl(neline): # if valid url next line -> source
                    # check for bold markdown ** **
                    if line[0] == "*":
                        line = line.rstrip()[2:-2]
                    else:
                        line = line.rstrip()

                    outline2 = (outline2 + " " * (pre_indentation + 4) + "<p>" + str(_id) + ". " + "<a href=\"" + neline.rstrip()
                                + "\" target=\"_blank\">" + line + "</a>")

                    try:
                        neneline=next(f)
                    except StopIteration:
                        outline2 = outline2 + "</p>\n"
                        archive = archive + outline2
                        _id = _id + 1
                        print("End of file")
                        break

                    while neneline.strip(): # all consecutive lines under a source are treated as urls
                        if not _isurl(neneline):
                            print(neneline.strip() + " not an url: skipped")
                            try:
                                neneline=next(f)
                                continue
                            except StopIteration:
                                print("End of file")
                                break

                        sourcename = ""
                        if "youku" in neneline:
                            sourcename = "优酷"
                        elif "iqiyi" in neneline:
                            sourcename = "爱奇艺"
                        elif "tudou" in neneline:
                            sourcename = "土豆"
                        elif "v.qq.com" in neneline:
                            sourcename = "腾讯"
                        elif "youtube" in neneline:
                            sourcename = "油管"
                        else:
                            sourcename = "其它"
                            #emsg = "Unknown video source: \n" + neneline
                            #raise ValueError(emsg)
                        outline2 = (outline2 + ", " + "<a href=\"" + neline.rstrip() + "\" target=\"_blank\">"
                                    + sourcename + "</a>")
                        try:
                            neneline=next(f)
                        except StopIteration:
                            print("End of file")
                            break

                    outline2 = outline2 + "</p>\n"
                    _id = _id + 1

                else: # if next line is not empty nor a source with a valid url
                    print("Error at line: " + line)
                    raise ValueError("Format error: 1 header + 1 empty line + continuous url lines")



            archive = archive + outline2

    archive = archive + 2 * " " + "</section>\n\n"
    archive = archive + "{% endblock %}\n"
    return archive

def build_toc(html_block):
    import re

    # decode title list
    toc = []
    stack = [toc]

    if html_block:
        html_list = html_block.split('\n')
        depth = 0
        for line in html_list:
            if '<h' in line:
                level = int(line.strip()[2]) - 1
                _title = re.search(r'>.*<', line).group(0)[1:-1]
                _id = re.search(r'id=".*"', line).group(0)[4:-1]
                depth = level if level > depth else depth
                d = {"level":level, 'title':_title, 'id':_id}
                d['sub'] = []
                while d['level'] < len(stack):
                    stack.pop()
                while d['level'] > len(stack):
                    stack.append(stack[-1][-1]['sub'])
                stack[-1].append(d)
    else:
        return None

    # creating title list
    def print_toc(toc):
        if not toc['sub']:
            indentation = (toc['level']-1) * 4 + 2
            return (" " * (indentation + 2) + '<li>'
                    + '<a href=\"#' + toc['id'] + '\">' + toc['title'] + '</a>'
                    + '</li>\n')

        indentation = 2 if toc['level'] == 0 else (toc['level']-1) * 4 + 2
        if toc['level'] == 0:
            tocSidebar = ""
            tocSidebar = " " * indentation + '<ul>\n'
        else:
            tocSidebar = " " * (indentation+2) + '<li>\n'
            tocSidebar = tocSidebar + " " * (indentation+4) + '<a href=\"#' + toc['id'] + '\">' + toc['title'] + '</a>\n'
            tocSidebar = tocSidebar + " " * (indentation+4) + '<ul>\n'

        for child in toc['sub']:
            tocSidebar = tocSidebar + print_toc(child)

        if toc['level'] == 0:
            tocSidebar = tocSidebar
            tocSidebar = tocSidebar + " " * indentation + '</ul>\n'
        else:
            tocSidebar = tocSidebar + " " * (indentation+4) + '</ul>\n'
            tocSidebar = tocSidebar + " " * (indentation+2) + '</li>\n'

        return tocSidebar

    toc = {'level':0, 'title': '', 'id':'', 'sub':stack[-1]}
    tocSidebar = "{% block pageSidebar%}\n" + print_toc(toc) + "{% endblock %}\n"

    return tocSidebar


def master_build(inputfile, outputfile):

    archive_string = build_archive_list(inputfile)
    sidebar_toc = build_toc(archive_string)
    head_str = ""
    with codecs.open(os.getcwd() + os.path.sep + "sources" + os.path.sep
                + inputfile.split(os.path.sep)[-1][:-4] + ".head", 'r', encoding="utf-8") as f:
        for line in f:
            head_str = head_str + line

    fo2 = codecs.open(outputfile, 'w', encoding="utf-8")
    fo2.write(head_str)
    fo2.write("\n")
    fo2.write(archive_string)
    fo2.write("\n")
    fo2.write(sidebar_toc)
    fo2.close()

def concatenate_files(sourcefolder):

    sourcefolder2 = sourcefolder + "补档模块" + os.path.sep
    filenames = [sourcefolder2 + "公演.txt", sourcefolder2 + "最新活动.txt", sourcefolder2 + "参与MV.txt", sourcefolder2 + "粉丝视频.txt",
                 sourcefolder2 + "团内荣誉.txt", sourcefolder2 + "演讲感言.txt", sourcefolder2 + "生日会.txt", sourcefolder2 + "其他.txt"]

    with codecs.open(sourcefolder + "补档.txt", 'w', encoding='utf-8') as fo:
        for fname in filenames:
            with codecs.open(fname, 'r', encoding='utf-8') as fi:
                for line in fi:
                    # remove UTF-BOM made by Windows notepad
                    if codecs.BOM_UTF8.decode('utf-8') in line:
                        line = line.replace(codecs.BOM_UTF8.decode('utf-8'),"")
                    fo.write(line)
            fo.write("\n\n")

    print("archive parts concatenated for 补档.txt!")

if __name__ == '__main__':

    sourcefolder = os.path.abspath(os.path.join(os.getcwd(), "..")) + os.path.sep + "文章" + os.path.sep

    # create 补档.txt
    concatenate_files(sourcefolder)

    # create njk flies for each archive
    master_build(sourcefolder + "补档.txt", os.getcwd() + os.path.sep + "show-archive.njk")
    master_build(sourcefolder + "unit展示.txt", os.getcwd() + os.path.sep + "unit-archive.njk")
    master_build(sourcefolder + "直播.txt", os.getcwd() + os.path.sep + "live-stream.njk")

    # move generated njk to app/ folder as template

    destination = os.path.abspath(os.path.join(os.getcwd(), "..")) + os.path.sep + "app" + os.path.sep
    shutil.copy2("show-archive.njk", destination + "show-archive.njk")
    shutil.copy2("unit-archive.njk", destination + "unit-archive.njk")
    shutil.copy2("live-stream.njk", destination + "live-stream.njk")
