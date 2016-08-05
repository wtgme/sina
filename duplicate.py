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


def check(last_rec, cur_rec):
    common = long_substr([last_rec[2], cur_rec[2]])
    key = re.sub('[0-9]+', '', common)
    if len(key)>5:
        print last_rec[0], cur_rec[0], last_rec[1].year-cur_rec[1].year, key


def process(row_list):
    leng = len(row_list)
    for i in xrange(0, leng):
        for j in xrange(i+1, leng):
            check(row_list[i], row_list[j])



def label_dum(file_name):
    idata = open_workbook(file_name)
    # odata = copy(idata)
    table = idata.sheet_by_index(0)
    row_num = table.nrows
    col_num = table.ncols
    # print row_num, col_num
    init_id = table.cell(1, 1)
    row_list = []

    for row_idx in range(1, row_num):
        # print table.cell(row_idx, 0), table.cell(row_idx, 2), xldate.xldate_as_datetime(table.cell(row_idx, 2).value, idata.datemode)
        if table.cell(row_idx, 1).value == init_id:
            row_list.append((table.cell(row_idx, 0).value,
                             xldate.xldate_as_datetime(table.cell(row_idx, 2).value, idata.datemode),
                             table.cell(row_idx, 6).value))
        else:
            if len(row_list) > 1:
                print init_id
                process(row_list)
            init_id = table.cell(row_idx, 1).value
            row_list = []
            row_list.append((table.cell(row_idx, 0).value,
                             xldate.xldate_as_datetime(table.cell(row_idx, 2).value, idata.datemode),
                             table.cell(row_idx, 6).value))

if __name__ == '__main__':
    label_dum('dup.xls')


