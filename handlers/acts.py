#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# Author: cuckoo
# Email: 454045250@qq.com
# Create Date: 2016-11-29


import time
import json
import datetime
import tornado.web
import requests
from bson import ObjectId
from core.web import HandlerBase
from framework.web import paging
from core.service import hand_acts
from framework.mvc.web import url, get_url
from framework.data.mongo import db, Document, DBRef


@url("/acts")
class Acts(HandlerBase):

    @tornado.web.authenticated
    def get(self):
        status = self.get_argument('status', '-1')
        key = self.get_argument('key', '')
        where = {}
        if key:
            where["$or"] = [ {'name' : { "$regex" : key }}, {'productId' : { "$regex" : key }}, {'venueName' : { "$regex" : key }} ]

        if status != '-1':
            where['status'] = int(status)
        acts = db.acts.find()
        self.context.key = key
        self.context.status = status
        self.context.acts = acts
        self.context.act = acts
        self.context.paging = paging.parse(self)
        self.context.act = db.acts.find(where) \
            .skip(paging.skip(self.context.paging)) \
            .limit(self.context.paging.size)
        self.context.paging.count = self.context.act.count()

        return self.template()


@url("/price")
class Price(HandlerBase):
    '''
        1,  查询场次
        2,  预约下单
    '''

    @tornado.web.authenticated
    def get(self):
        id = self.get_argument('id', '') or None
        act = db.acts.find_one({ '_id' : ObjectId(id) })

        try:
            self.context.act = act
            self.context.price = "price" in act and act.price or []
        except Exception, e:
            print e

        return self.template()

    @tornado.web.authenticated
    def post(self):
        productId = self.get_argument("productId", "")
        minprice = self.get_argument("minprice", "")
        maxprice = self.get_argument("maxprice", "")
        count = self.get_argument("count", "")
        starttime = self.get_argument("starttime", "")
        endtime = self.get_argument("endtime", "")

        if not starttime or not endtime:
            return self.json({"status": "faild", "desc": "时间不能留空!"})

        if not count:
            return self.json({"status": "faild", "desc": "购买数量不能留空!"})

        if not productId:
            return self.json({"status": "faild", "desc": "获取ID异常!"})
        try:
            minprice = int(minprice)
            maxprice = int(maxprice)
            count = int(count)
        except:
            return self.json({"status": "faild", "desc": "金额和数量必须为整数!"})

        if minprice > maxprice:
            return self.json({"status": "faild", "desc": "最小金额不能大于最大金额!"})

        if starttime > endtime:
            return self.json({"status": "faild", "desc": "开始时间不能大于结束时间!"})

        try:
            starttime = starttime + ":00"
            endtime = endtime + ":00"
            stime = time.strptime(starttime, "%Y-%m-%d %H:%M:%S")
            etime = time.strptime(endtime, "%Y-%m-%d %H:%M:%S")
            starttimestamp = int(time.mktime(stime))
            endtimestamp= int(time.mktime(etime))
        except Exception, e:
            print e

        current_user = self.context.current_user

        try:
            act = db.acts.find_one({ "productId" : productId })

            # 添加分场id
            price = "price" in act and act.price or []

            productPlayIds = []
            if price:
                for i in price:
                    try:
                        p = int(i.price)
                        if minprice <= p <= maxprice:
                            productPlayIds.append(i.productPlayId)
                    except:
                        print e

            order = Document()
            order.act = act
            order.productId = productId
            order.minprice = minprice
            order.maxprice = maxprice
            order.count = count
            order.starttime = datetime.datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
            order.endtime = datetime.datetime.strptime(endtime, "%Y-%m-%d %H:%M:%S")
            order.starttimestamp = starttimestamp
            order.endtimestamp = endtimestamp
            order.status = -1
            order.site = "yongle"
            order.log = [
                { "addon" : datetime.datetime.now(), "desc" : "预约成功。", "operator" : current_user.username }
            ]

            order.productPlayIds = productPlayIds
            order.user = current_user
            order.created = datetime.datetime.now()

            db.order.insert_one(order)

            self.system_record(current_user._id, 2, "订单预约", "")
            return self.json({"status": "ok"})
        except:
            return self.json({"status": "faild", "desc": "未知错误!"})


@url("/acts/update")
class ActsUpdate(HandlerBase):
    def post(self):
        try:
            hand_acts.check_acts()
            current_user = self.context.current_user
            self.system_record(current_user._id, 5, "数据更新", "")
            return self.json({"status": "ok"})
        except:
            return self.json({"status": "faild", "desc": "刷新失败!"})