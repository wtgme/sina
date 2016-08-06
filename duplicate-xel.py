# -*- coding: utf-8 -*-
"""
Created on 15:09, 05/08/16

@author: wt
"""
import xlwt
import re
from xlrd import open_workbook,xldate
from xlutils.copy import copy
from datetime import datetime


def is_substr(find, data):
        if len(data) < 1 and len(find) < 1:
            return False
        for i in range(len(data)):
            if find not in data[i]:
                return False
        return True


def long_substr(data):
    substr = ''
    if len(data) > 1 and len(data[0]) > 0:
        for i in range(len(data[0])):
            for j in range(len(data[0])-i+1):
                if j > len(substr) and is_substr(data[0][i:i+j], data):
                    substr = data[0][i:i+j]
    return substr


def check(last_rec, cur_rec, mode):
    common = long_substr([last_rec[6], cur_rec[6]])
    key = re.sub('[0-9]+', '', common)
    t1, t2 = xldate.xldate_as_datetime(last_rec[2], mode), xldate.xldate_as_datetime(cur_rec[2], mode)
    if len(key)>=7 and abs(t1.year-t2.year)<=2:
        return str(int(cur_rec[0]))+u':'+key
    else:
        return u'None'


def process(otable, mode, row_index, row_list):
    leng = len(row_list)
    for i in xrange(0, leng):
        reci = row_list[i]
        col_index = 0
        for col_index, cell_value in enumerate(reci):
            otable.write(row_index, col_index, cell_value)
        for j in xrange(i+1, leng):
            recj = row_list[j]
            res = check(reci, recj, mode)
            if res != 'None':
                otable.write(row_index, col_index, res)
                col_index += 1
        row_index += 1


def label_dum(file_name,outfile):
    idata = open_workbook(file_name)
    table = idata.sheet_by_index(0)
    odata = xlwt.Workbook()
    otable = odata.add_sheet('Sheet1', cell_overwrite_ok=True)
    row_index = 0
    row_num = table.nrows

    for col_index, cell_value in enumerate(table.row_values(0)):
        otable.write(row_index, col_index, cell_value)
    row_index += 1

    init_id = table.cell(1, 1)
    row_list = []
    for row_idx in range(1, row_num):
        if table.cell(row_idx, 1).value == init_id:
            row_list.append(table.row_values(row_idx))
        else:
            if len(row_list) > 1:
                process(otable, idata.datemode, row_index, row_list)
            else:
                for col_index, cell_value in enumerate(table.row_values(row_idx)):
                    otable.write(row_index, col_index, cell_value)
            row_index += len(row_list)
            init_id = table.cell(row_idx, 1).value
            row_list = []
            row_list.append(table.row_values(row_idx))
    if len(row_list) > 1:
        process(otable, idata.datemode, row_index, row_list)
    else:
        for col_index, cell_value in enumerate(table.row_values(row_num-1)):
            otable.write(row_index, col_index, cell_value)
    row_index += len(row_list)

    odata.save(outfile)

if __name__ == '__main__':
    label_dum('dup.xls', 'out.xls')


