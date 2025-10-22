# encoding: utf-8
import os
import urllib.error
import urllib.request
import re
import xlwt
from bs4 import BeautifulSoup
from xlrd import open_workbook
from xlutils.copy import copy
from datetime import datetime
import sys
import time
import random


class Spider:
    HEADER_COLUMNS = [
        '记录ID',
        '股票代号',
        '公告日期',
        '处分类型',
        '标题',
        '相关法规',
        '文件批号',
        '批复原因',
        '批复内容',
        '处理人',
        '网络链接',
        '本地链接',
    ]

    def __init__(self, fileName):
        try:
            data = open_workbook(fileName)
            table = data.sheet_by_index(0)
            self.beginRow = 1
        # nrows = table.nrows
        # if nrows > 0:
        # 	self.beginRow = nrows

        except IOError as e:
            punishFile = xlwt.Workbook()
            table = punishFile.add_sheet('Sheet1', cell_overwrite_ok=True)
            for col_idx, col_name in enumerate(self.HEADER_COLUMNS):
                table.write(0, col_idx, col_name)

            punishFile.save(fileName)
            self.beginRow = 1

    def apply_header(self, table):
        for col_idx, col_name in enumerate(self.HEADER_COLUMNS):
            table.write(0, col_idx, col_name)

    @staticmethod
    def clean_text(value):
        if value is None:
            return ''
        value = value.replace('\xa0', ' ')
        return re.sub(r'\s+', ' ', value).strip()

    @staticmethod
    def sanitize_filename(value):
        clean_value = Spider.clean_text(value)
        return re.sub(r'[\\/*?\:"<>|]', '_', clean_value)

    def parse_page(self, html_text):
        soup = BeautifulSoup(html_text, 'html.parser')
        company_tag = soup.select_one('.toolbartop h1 a')
        company_name = self.clean_text(company_tag.get_text()) if company_tag else ''

        records = []
        data_table = soup.select_one('#collectFund_1')
        if not data_table:
            return company_name, records

        for thead in data_table.find_all('thead'):
            th = thead.find('th')
            if not th:
                continue

            header_text = self.clean_text(th.get_text(' ', strip=True))
            match = re.search(r'(.+?)公告日期[:：]\s*(\d{4}-\d{2}-\d{2})', header_text)
            if not match:
                continue

            punish_type = self.clean_text(match.group(1))
            try:
                record_date = datetime.strptime(match.group(2), '%Y-%m-%d')
            except ValueError:
                continue

            title = ''
            law = ''
            file_no = ''
            reason = ''
            reply = ''
            handler = ''

            for sibling in thead.next_siblings:
                sibling_name = getattr(sibling, 'name', None)
                if sibling_name == 'thead':
                    break
                if sibling_name != 'tr':
                    continue

                cells = sibling.find_all('td')
                if not cells:
                    continue

                if len(cells) == 1 and cells[0].get('colspan') == '2':
                    break

                if len(cells) < 2:
                    continue

                label = self.clean_text(cells[0].get_text())
                value = self.clean_text(cells[1].get_text(separator=' '))

                if not label:
                    continue

                if label == '标题':
                    title = value
                elif label == '相关法规':
                    law = value
                elif label in ('文件批号', '批复文号', '文件批号/文号'):
                    file_no = value
                elif label in ('违规行为', '批复原因', '批复原因/违规行为'):
                    reason = value
                elif label in ('批复内容', '处理结果', '处理决定'):
                    reply = value
                elif label in ('处理人', '处理机构'):
                    handler = value

            if not reason:
                reason = title

            records.append({
                'date': record_date,
                'punish_type': punish_type,
                'title': title,
                'law': law,
                'file_no': file_no,
                'reason': reason,
                'reply_content': reply,
                'handler': handler,
                'company': company_name or title,
            })

        return company_name, records

    def GetPage(self, urlNumber, table, fileDir):
        punishUrl = "http://vip.stock.finance.sina.com.cn/corp/go.php/vGP_GetOutOfLine/stockid/" + urlNumber + ".phtml?qq-pf-to=pcqq.c2c"
        print(punishUrl)
        
        # Add headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        }
        
        # Retry logic
        max_retries = 3
        page = None
        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(punishUrl, headers=headers)
                response = urllib.request.urlopen(req, timeout=30)
                page = response.read()
                break
            except urllib.error.HTTPError as e:
                print(f"HTTP Error {e.code} on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # Exponential backoff: 5, 10, 15 seconds
                    print(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    print(f"Failed to fetch {urlNumber} after {max_retries} attempts")
                    return
            except Exception as e:
                print(f"Error fetching page: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    return

        if page is None:
            return
        
        # print(page)
        unicodePage = page.decode("gb2312", 'ignore')
        utf8Page = unicodePage

        company_name, records = self.parse_page(utf8Page)
        if not records:
            print('结构化数据未找到，跳过该页面')
            return

        '''Save HTML files'''
        tempPage = page.replace(b"href=\"/corp", b"href=\"corp")
        newPage = tempPage.replace(b"src=\"/corp", b"src=\"corp")

        os.makedirs(fileDir, exist_ok=True)
        primary_record = records[0]
        fileNameHtml = f"{urlNumber}_{self.sanitize_filename(primary_record['company'])}_{primary_record['date'].strftime('%Y-%m-%d')}.html"
        filePathHtml = os.path.join(fileDir, fileNameHtml)
        with open(filePathHtml, 'wb') as htmlFile:
            htmlFile.write(newPage)

        '''Write Excel record'''
        date_format = xlwt.XFStyle()
        date_format.num_format_str = 'yyyy/mm/dd'

        row = self.beginRow

        for record in records:
            self.recording(record, date_format, filePathHtml, punishUrl, row, table, urlNumber)
            row += 1

        self.beginRow = row

    def recording(self, record, date_format, filePathHtml, punishUrl, row, table, urlNumber):
        table.write(row, 0, row)
        table.write(row, 1, urlNumber)
        table.write(row, 2, record['date'], date_format)
        table.write(row, 3, record['punish_type'])
        table.write(row, 4, record['title'])
        table.write(row, 5, record['law'])
        table.write(row, 6, record['file_no'])
        table.write(row, 7, record['reason'])
        table.write(row, 8, record['reply_content'])
        table.write(row, 9, record['handler'])
        table.write(row, 10, punishUrl + ' ')
        table.write(row, 11, filePathHtml + ' ')


def read_run(codeName, fileName, fileDir):
    spider = Spider(fileName)
    rb = open_workbook(fileName)
    wb = copy(rb)
    table = wb.get_sheet(0)
    spider.apply_header(table)

    with open(codeName, 'r') as fo:
        for line in fo.readlines():
            print(line.strip())
            spider.GetPage(line.strip(), table, fileDir)
            # Add delay between requests to avoid rate limiting
            delay = random.uniform(2, 5)  # Random delay between 2-5 seconds
            print(f"Waiting {delay:.2f} seconds before next request...")
            time.sleep(delay)

    wb.save(fileName)


if __name__ == '__main__':
    read_run(sys.argv[1], sys.argv[2], sys.argv[3])
# read_run('shenzhen_code', 'shenzhen.xls', 'shenzhen')
# python xinlang_doc_py3.py code.txt sina_chufa_2025_10.xls sina
