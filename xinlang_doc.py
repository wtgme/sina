#encoding: utf-8
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
			# nrows = table.nrows
			# if nrows > 0:
			# 	self.beginRow = nrows

		except IOError, e:
			punishFile = xlwt.Workbook()
			table = punishFile.add_sheet('Sheet1', cell_overwrite_ok=True)
			table.write(0, 0, u'股票代号')
			table.write(0, 1, u'公告日期')
			table.write(0, 2, u'公司名称')
			table.write(0, 3, u'相关法规')
			table.write(0, 4, u'处分类型')
			table.write(0, 5, u'违规行为')
			table.write(0, 6, u'批复内容')
			table.write(0, 7, u'处理人')

			punishFile.save(fileName)
			self.beginRow = 1

	def GetPage(self, urlNumber, table):
		punishUrl = "http://vip.stock.finance.sina.com.cn/corp/go.php/vGP_GetOutOfLine/stockid/" + urlNumber + ".phtml?qq-pf-to=pcqq.c2c"
		response = urllib2.urlopen(punishUrl)
		page = response.read()
		#print page
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

		date_format = xlwt.XFStyle()
		date_format.num_format_str = 'yyyy/mm/dd'

		i = 0
		row = self.beginRow
		while i < len(illegalBehaviors):
			# print urlNumber, "".join(companys[i].decode('utf-8').split())
			table.write( row, 0, urlNumber)
			table.write( row, 1, datetime.strptime(times[i], '%Y-%m-%d'), date_format)
			table.write( row, 2, "".join(companys[i].decode('utf-8').split()))
			table.write( row, 3, "".join(laws[i].decode('utf-8').replace('&nbsp;', '').split()))
			table.write( row, 4, "".join(punishTypes[i].decode('utf-8').replace('&nbsp;', '').split()))
			table.write( row, 5, "".join(illegalBehaviors[i].decode('utf-8').replace('&nbsp;', '').split()))
			table.write( row, 6, "".join(replyContents[i].decode('utf-8').replace('&nbsp;', '').split()))
			table.write( row, 7, "".join(handlers[i].decode('utf-8').split()))
			row = row + 1
			i = i + 1

		self.beginRow = row


def read_run(codeName, fileName):
	spider = Spider(fileName)
	rb = open_workbook(fileName)
	wb = copy(rb)
	table = wb.get_sheet(0)

	with open(codeName, 'r') as fo:
		for line in fo.readlines():
			print line.strip()
			spider.GetPage(line.strip(), table)

	wb.save(fileName)

if __name__ == '__main__':
	read_run(sys.argv[1], sys.argv[2])
	# read_run('shenzhen_code', 'shenzhen.xls')
