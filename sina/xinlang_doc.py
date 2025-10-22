# encoding: utf-8
import urllib2
import re
import xlwt
from xlrd import open_workbook
from xlutils.copy import copy
from datetime import datetime
import sys


class Spider:
    def __init__(self, fileName):
        try:
            data = open_workbook(fileName)
            table = data.sheet_by_index(0)
            self.beginRow = 1
        # nrows = table.nrows
        # if nrows > 0:
        # 	self.beginRow = nrows

        except IOError, e:
            punishFile = xlwt.Workbook()
            table = punishFile.add_sheet('Sheet1', cell_overwrite_ok=True)
            table.write(0, 0, u'记录ID')
            table.write(0, 1, u'股票代号')
            table.write(0, 2, u'公告日期')
            table.write(0, 3, u'公司名称')
            table.write(0, 4, u'相关法规')
            table.write(0, 5, u'处分类型')
            table.write(0, 6, u'违规行为')
            table.write(0, 7, u'批复内容')
            table.write(0, 8, u'处理人')
            table.write(0, 9, u'网络链接')
            table.write(0, 10, u'本地链接')
            table.write(0, 11, u'Common_Strs')

            punishFile.save(fileName)
            self.beginRow = 1

    def is_substr(self, find, data):
        if len(data) < 1 and len(find) < 1:
            return False
        for i in range(len(data)):
            if find not in data[i]:
                return False
        return True

    def long_substr(self, data):
        substr = ''
        if len(data) > 1 and len(data[0]) > 0:
            for i in range(len(data[0])):
                for j in range(len(data[0])-i+1):
                    if j > len(substr) and self.is_substr(data[0][i:i+j], data):
                        substr = data[0][i:i+j]
        return substr

    def check(self, last_rec, cur_rec):
        common = self.long_substr([last_rec[2], cur_rec[2]])
        key = re.sub('[0-9]+', '', common)
        if (last_rec[0].year == cur_rec[0].year) & \
                (last_rec[1] == cur_rec[1]) & (len(key)>=5):
            return common
        else:
            return 'None'

    def GetPage(self, urlNumber, table, fileDir):
        punishUrl = "http://vip.stock.finance.sina.com.cn/corp/go.php/vGP_GetOutOfLine/stockid/" + urlNumber + ".phtml?qq-pf-to=pcqq.c2c"
        response = urllib2.urlopen(punishUrl)
        page = response.read()
        # print page
        unicodePage = page.decode("gb2312", 'ignore')
        utf8Page = unicodePage.encode("utf-8")

        times = re.findall(r'违规记录&nbsp;&nbsp;公告日期:(.*?)</th>', utf8Page, re.S)
        if times == []:
            print 'null page'
            return

        companys = re.findall(r'公司名称</strong></td><td>(.*?)</td>', utf8Page, re.S)
        laws = re.findall(r'相关法规</strong></td><td>(.*?)</td>', utf8Page, re.S)
        punishTypes = re.findall(r'处分类型</strong></td><td>(.*?)</td>', utf8Page, re.S)
        illegalBehaviors = re.findall(r'违规行为</strong></td><td>(.*?)</td>', utf8Page, re.S)
        replyContents = re.findall(r'批复内容</strong></td><td>(.*?)</td>', utf8Page, re.S)
        handlers = re.findall(r'处理人</strong></td><td>(.*?)</td>', utf8Page, re.S)

        '''Save HTML files'''
        tempPage = page.replace("href=\"/corp", "href=\"corp")
        newPage = tempPage.replace("src=\"/corp", "href=\"corp")
        fileNameHtml = urlNumber + '_' + "".join(companys[0].decode('utf-8').split()) + '_' + times[0] + ".html"
        filePathHtml = fileDir + "/" + fileNameHtml
        htmlFile = open(filePathHtml, 'w')
        htmlFile.write(newPage)
        htmlFile.close()

        '''Write Excel record'''
        date_format = xlwt.XFStyle()
        date_format.num_format_str = 'yyyy/mm/dd'

        i = 0
        row = self.beginRow
        temp_record = self.recording(companys, date_format, filePathHtml, handlers, i, illegalBehaviors, laws,
                                     punishTypes,
                                     punishUrl, replyContents, row, table, times, urlNumber)
        table.write(row, 11, 'None')
        i = i + 1
        row = row + 1
        while i < len(illegalBehaviors):
            # print urlNumber, "".join(companys[i].decode('utf-8').split())
            record = self.recording(companys, date_format, filePathHtml, handlers, i, illegalBehaviors, laws,
                                    punishTypes,
                                    punishUrl, replyContents, row, table, times, urlNumber)
            comm = self.check(temp_record, record)
            table.write(row, 11, comm)
            temp_record = record
            row = row + 1
            i = i + 1

        self.beginRow = row

    def recording(self, companys, date_format, filePathHtml, handlers, i, illegalBehaviors, laws, punishTypes,
                  punishUrl, replyContents, row, table, times, urlNumber):
        table.write(row, 0, row)
        table.write(row, 1, urlNumber)
        table.write(row, 2, datetime.strptime(times[i], '%Y-%m-%d'), date_format)
        table.write(row, 3, "".join(companys[i].decode('utf-8').replace('&nbsp;', '').split()))
        table.write(row, 4, "".join(laws[i].decode('utf-8').replace('&nbsp;', '').split()))
        table.write(row, 5, "".join(punishTypes[i].decode('utf-8').replace('&nbsp;', '').split()))
        table.write(row, 6, "".join(illegalBehaviors[i].decode('utf-8').replace('&nbsp;', '').split()))
        table.write(row, 7, "".join(replyContents[i].decode('utf-8').replace('&nbsp;', '').split()))
        table.write(row, 8, "".join(handlers[i].decode('utf-8').replace('&nbsp;', '').split()))
        table.write(row, 9, punishUrl + ' ')
        table.write(row, 10, filePathHtml + ' ')
        return (datetime.strptime(times[i], '%Y-%m-%d'),
                "".join(punishTypes[i].decode('utf-8').replace('&nbsp;', '').split()),
                "".join(illegalBehaviors[i].decode('utf-8').replace('&nbsp;', '').split()))


def read_run(codeName, fileName, fileDir):
    spider = Spider(fileName)
    rb = open_workbook(fileName)
    wb = copy(rb)
    table = wb.get_sheet(0)

    with open(codeName, 'r') as fo:
        for line in fo.readlines():
            print line.strip()
            spider.GetPage(line.strip(), table, fileDir)

    wb.save(fileName)


if __name__ == '__main__':
    read_run(sys.argv[1], sys.argv[2], sys.argv[3])
# read_run('shenzhen_code', 'shenzhen.xls', 'shenzhen')