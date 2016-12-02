#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os
import sys
sys.path.append(os.path.abspath("../../"))
reload(sys)
sys.setdefaultencoding('utf-8')

import time
import json
import pymongo
import requests
import datetime
from bson import ObjectId
from framework.data.mongo import db, Document, DBRef


'''
    status: 
        0 >> 正常 >> 里面也会有状态为预售的票, 也会有其他纪念品, 支付时一定要注意
        1 >> 预售
        2 >> 
        3 >> 待定(未售)
'''

def checkmobile(mobile):
    url = 'http://api.ip138.com/mobile/?mobile={0}&token=6dd6780e5a8fb9020345c031ae0aac0c'.format(mobile)
    try:
        r = requests.get(url, timeout=5)
        result = json.loads(r.text)

        if result['ret'] == "ok":
            data = result['data']
            info = "-".join([ i for i in data ])
        else:
            info = "查询失败"
    except Exception, e:
        print e
        info = "查询失败"

    return info

if __name__ == '__main__':
    info = checkmobile("13929198406")
    print info