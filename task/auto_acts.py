#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os
import sys
sys.path.append(os.path.abspath("../"))
reload(sys)
sys.setdefaultencoding('utf-8')

import time
import json
import pymongo
import requests
import schedule
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

def check_acts():
    url = 'http://api.228.cn/products/query?access_phone_type=android&app_version=My4yLjY%3d&sort_type=1&page_size=0&page_no=1&nc=300'
    r = requests.get(url)
    result = json.loads(r.text)

    code = result['result']['code']
    try:
        acts_list = []
        if code == 0:
            totalCount = result['data']['page']['totalCount']
            check_url = 'http://api.228.cn/products/query?access_phone_type=android&app_version=My4yLjY%3d&sort_type=1&page_size={0}&page_no=1&nc=300'.format(totalCount)
            r = requests.get(check_url)
            result = json.loads(r.text)
            code = result['result']['code']
            if code == 0:
                # 删除旧数据
                db.acts.drop()
                records = result['data']['records']
                for k in records:
                    act = Document()
                    # 名称
                    act.name = k['name']
                    # 状态
                    act.status = k['status']
                    # 开始时间
                    act.beginDate = k['beginDate']
                    # 结束时间
                    act.finishDate = k['finishDate']
                    # 图片
                    act.imgPath = k['imgPath']
                    # 演出地址
                    act.venueName = k['venueName']
                    # id
                    act.productId = k['productId']
                    # 收集时间
                    act.created = datetime.datetime.now()

                    db.acts.insert_one(act)

    except Exception, e:
        print e


def job():
    check_acts()


if __name__ == '__main__':
    schedule.every(600).seconds.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)