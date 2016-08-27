# -*- coding: utf-8 -*-
"""
Created on 11:16 AM, 8/27/16

@author: tw
Spider for http://quote.cfi.cn/quote.aspx?stockid=3&contenttype=zdsj&jzrq=2001
"""

import re
from lxml import html
import requests
from datetime import datetime
import sys


def GetPage(stockid, year, ido):
    punishUrl = 'http://quote.cfi.cn/quote.aspx?stockid=' + stockid + '&contenttype=zdsj&jzrq=' + year
    page = requests.get(punishUrl)
    # print page.content
    # unicodePage = page.decode("gb2312", 'ignore')
    # utf8Page = unicodePage.encode("utf-8")
    tree = html.fromstring(page.content)

    '''Remove 'tbody' in Xpath obatained from browser'''
    records = tree.xpath('//*[@id="tabh"]/tr')
    # print records
    if len(records) == 0:
        print 'null page'
        return
    for record in records[2:-1]:
        '''using . for current element'''
        time = record.xpath('./td[1]/a/text()')[0].encode("utf-8")
        topic = record.xpath('./td[2]/text()')[0].encode("utf-8")
        content = record.xpath('./td[3]/text()')[0].encode("utf-8")
        print ido + '\t' + time + '\t' + ''.join(topic.split()) + '\t' + ''.join(content.split())

        # print datetime.strptime(time, '%Y-%m-%d')
        # print ''.join(topic.split())
        # print ''.join(content.split())



def read_need():
    idlist, idmap = [], {}
    with open('zhongcai.txt', 'r') as fo:
        for line in fo.readlines():
            tokens = line.strip().split()
            for token in tokens:
                v = re.findall(r'\d+', token)[0]
                idmap[v] = len(idmap) + 1
    with open('need.txt', 'r') as fo:
        for line in fo.readlines():
            idlist.append(line.strip())
    zxid = []
    for uid in idlist:
        stockid = idmap.get(uid, None)
        if stockid:
            zxid.append((uid, stockid))
        else:
            pass

    return zxid


def read_run(idlist, years):
    for ido, idxc in idlist:
        for year in years[::-1]:
            # print '------------------------------------'
            GetPage(str(idxc), str(year), ido)


if __name__ == '__main__':
    years = range(2001, 2017)
    idlist = read_need()
    read_run(idlist, years)
# read_run('shenzhen_code', 'shenzhen.xls', 'shenzhen')
