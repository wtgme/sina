# -*- coding: utf-8 -*-
"""
Created on 13:15, 14/07/16

@author: wt
"""

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

print long_substr(['你公司董事会于2012年3月8日发布公告，审议通过控股子公司深圳融发投资有限公司（以下称“融发投资”）向金融机构申请贷款项目。由于该等贷款项目拟以融发投资主要资产―皇庭国商购物广场项目房产证提供抵押担保，根据本所《股票上市规则》第9.3条相关规定，你公司董事会将该贷款事项提交股东大会审议，并发出2012年临时股东大会通知。近日，我所收到投资者来电、来函反映，要求你公司对将于3月23日召开的2012年第二次临时股东大会提供网络投票表决方式，以利于投资者就相关议案进行投票表决。',
                   '深你公司董事会于3月7日向我部报送关于审批控股子公司向金融机构贷款的第六届董事会2012年第二次临时董事会决议公告等相关文件。根据该次董事会决议，你公司控股子公司深圳融发投资有限公司（以下简称“融发投资”）拟向金融机构申请总金额不超过17亿元人民币的借款，主要用于偿还融发公司借款、补充公司日常营运资金，做好皇庭国商购物广场项目（为公司原晶岛国商购物中心项目）开业前的装修、招商及前期推广工作。上述借款采用融发投资的开发项目进行抵押担保，你公司董事长郑康豪先生及其控股的深圳市皇庭地产集团有限公司提供连带责任保证担保，融发投资其他股东提供相应担保。但本所交易系统显示你公司董事长郑康豪在2012年3月5日买入你公司B股117602股。'])