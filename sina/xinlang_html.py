#encoding: utf-8
import urllib2
import re
import sys

class Spider:

	def GetPage(self, urlNumber, fileDir):
		punishUrl = "http://vip.stock.finance.sina.com.cn/corp/go.php/vGP_GetOutOfLine/stockid/" + urlNumber + ".phtml?qq-pf-to=pcqq.c2c"
		response = urllib2.urlopen(punishUrl)
		page = response.read()
		unicodePage = page.decode("gb2312", 'ignore')
		utf8Page = unicodePage.encode("utf-8")

		times = re.findall(r'违规记录&nbsp;&nbsp;公告日期:(.*?)</th>', utf8Page, re.S)
		if times == []:
			print 'null page'
			return

		companys = re.findall(r'公司名称</strong></td><td>(.*?)</td>', utf8Page, re.S)
		print "".join(companys[0].decode('utf-8').split())

		tempPage = page.replace("href=\"/corp", "href=\"corp")
		newPage = tempPage.replace("src=\"/corp", "href=\"corp")

		fileName = urlNumber + '_' + "".join(companys[0].decode('utf-8').split()) + '_' + times[0] + ".html"
		filePath = fileDir + "/" + fileName

		htmlFile = open(filePath, 'w')
		htmlFile.write(newPage)
		htmlFile.close()


def run(codeName, fileDir):
	spider = Spider()
	with open(codeName, 'r') as fo:
		for line in fo.readlines():
			print line.strip()
			spider.GetPage(line.strip(), fileDir)


if __name__ == '__main__':
	run(sys.argv[1], sys.argv[2])
	# run('shenzhen_code',  'shenzhen')