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
    url = 'http://api.228.cn/products/query?access_phone_type=android&app_version=My4yLjY%3D&token=&site_id=&product_category_id=&time_range=&sort_type=1&page_size=0&page_no=1&nc=300'
    headers = {'User-Agent':''}
    r = requests.get(url, headers=headers)

    result = json.loads(r.text)

    code = result['result']['code']
    try:
        acts_list = []
        if code == 0:
            totalCount = result['data']['page']['totalCount']
            # 每次100条
            count = int(totalCount / 100)
            # 删除旧数据
            db.acts.drop()

            for i in range(1000):
                print "开始第{0}次100条查询".format(i+1)
                check_url = 'http://api.228.cn/products/query?access_phone_type=android&app_version=My4yLjY%3D&token=&site_id=&product_category_id=&time_range=&sort_type=1&page_size=100&page_no={0}&nc=300'.format(i+1)
                r = requests.get(check_url, headers=headers)
                result = json.loads(r.text)
                code = result['result']['code']
                if code == 0:
                    records = result['data']['records']
                    if len(records) == 0:
                        break
                    else:
                        for k in records:
                            act = Document()
                            act._id = ObjectId()
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

                            # 收集场次具体信息
                            pro_url = "http://api.228.cn/product_plays/all_by_product?access_phone_type=android&app_version=My4yLjY=&product_id={0}".format(k['productId'])
                            rs = requests.get(pro_url, headers=headers)
                            result1 = json.loads(rs.text)
                            code1 = result1['result']['code']
                            if code1 == 0:
                                infos = Document()
                                # 查询时间
                                infos.timestamp = result1['result']['timestamp']

                                data1 = result1['data']
                                for d in data1:                  
                                    prices = d['prices']

                                    price_list = []
                                    for p in prices:
                                        dic = Document()
                                        # 分场次的状态
                                        dic.status = p['status']
                                        # 分场次的ID
                                        dic.productPlayId = p['productPlayId']
                                        # 分场最大购买数量
                                        dic.buylimit = p['buylimit']
                                        # 分场的开场时间
                                        dic.time = p['time']
                                        # 库存
                                        dic.num = p['num']
                                        # 金额
                                        dic.price = p['price']
                                        # 演出日期
                                        dic.playdate = p['playdate']
                                        # 备注
                                        dic.playinfo = p['playinfo']

                                        # 存数据
                                        price_list.append(dic)

                                    db.acts.find_one_and_update({ "_id" : act._id }, { "$set" : { "price" : price_list } })

                            else:
                                pass
                print "完成第{0}次100条查询".format(i+1)
        else:
            print "获取失败"
    except Exception, e:
        print e


if __name__ == '__main__':
    check_acts()