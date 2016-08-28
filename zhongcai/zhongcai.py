# -*- coding: utf-8 -*-
"""
Created on 11:16 AM, 8/27/16

@author: tw
Spider for http://quote.cfi.cn/quote.aspx?stockid=3&contenttype=zdsj&jzrq=2001
"""

from lxml import html
import requests
from datetime import datetime


def start():
    startUrl = 'http://quote.cfi.cn/stockList.aspx'
    page = requests.get(startUrl)
    tree = html.fromstring(page.content)

    stocks_lists = tree.xpath('//*[@id="divcontent"]/table/tr')
    for stocks_list in stocks_lists:
        stocks = stocks_list.xpath('./td')
        for stock in stocks:
            stockUrl = stock.xpath('./a/@href')[0]
            stock_home(stockUrl)


def stock_home(stockUrl):
    home = requests.get('http://quote.cfi.cn/'+stockUrl)
    tree = html.fromstring(home.content)
    event = tree.xpath('//*[@id="nodea32"]/nobr/a/@href')[0]
    tokens = event.split('/')
    stockid = tokens[2]
    ido = tokens[-1].replace('.html', '')
    print event, stockid, ido
    years = range(2001, 2017)
    for year in years[::-1]:
        GetPage(stockid, str(year), ido)


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


if __name__ == '__main__':
    start()
