#encoding: utf-8
import urllib2
import re
import xlwt
from xlrd import open_workbook
from xlutils.copy import copy
from datetime import datetime

def parse_page(url):
	response = urllib2.urlopen(url)
	page = response.read()
	unicodePage = page.decode("gb2312", 'ignore')
	utf8Page = unicodePage.encode("utf-8")

	codes = re.findall(r'\" target=\"_blank\">(\d*?)</a>', utf8Page, re.S)
	for code in codes:
		print code

if __name__ == '__main__':
	for i in xrange(22):
		parse_page('https://biz.sse.com.cn/sseportal/webapp/datapresent/SSEQueryStockInfoInitAct?reportName=BizCompStockInfoRpt&PRODUCTID=&PRODUCTJP=&PRODUCTNAME=&keyword=&CURSOR='+str(50*i+1)+'&tab_flg=1')