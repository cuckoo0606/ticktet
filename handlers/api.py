#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# Author: cuckoo
# Email: 454045250@qq.com
# Create Date: 2016-11-29


import json
import time
import datetime
import tornado.web
from bson import ObjectId
from core.web import HandlerBase
from framework.web import paging
from framework.util.security import md5
from framework.mvc.web import url, get_url
from framework.data.mongo import db, Document, DBRef


def message(msg, status=-1, data=""):
    return { "status" : status, "msg" : msg, "data" : data }


@url("/api/task")
class ApiTask(HandlerBase):

    '''
        获取订单
            1,  status : -1
            2,  site : [yongle, damai]
            3,  时间判断
            4,  校验: sign :  md5(年月日+类型+caonima)
    '''

    def code(self):
        date = time.strftime('%Y%m%d',time.localtime())

        return md5(date)

    def get(self):
        sign = self.get_argument("sign", "")

        if not sign:
            return self.json(message("not sign"))

        code = self.code()

        if code != sign:
            return self.json(message("invalid sign"))

        now = datetime.datetime.now()

        try:
            where = {}
            where['status'] = -1
            where['starttime'] = { "$lte" : now }
            where['endtime'] = { "$gte" : now }

            order = db.order.find_one(where)

            if order:
                result = Document()
                result.id = str(order._id)
                result.count = order.count
                result.productId = order.productId
                result.productPlayIds = order.productPlayIds
                result.maxprice = order.maxprice
                result.minprice = order.minprice
                result.starttimestamp = order.starttimestamp
                result.endtimestamp = order.endtimestamp
                result.site = order.site

                return self.json(message("success", 0, result))
            else:
                return self.json(message("order is None", 404))
        except:
            return self.json(message("error system"))


@url("/api/update")
class ApiUpdate(HandlerBase):

    '''
        hashlib.md5(src).hexdigest()
        更新订单状态
            1,  状态 -1 >> 1, 添加log
            2,  校验: sign :  md5(年月日+id)
    '''

    def code(self, id):
        date = time.strftime('%Y%m%d',time.localtime())
        st = "{0}{1}".format(date, id)

        return md5(st)

    def post(self):
        id = self.get_argument("id", "") or None
        sign = self.get_argument("sign", "")

        code = self.code(id)
        if code != sign:
            return self.json(message("invalid sign"))

        try:
            order = db.order.find_one({ "_id" : ObjectId(id), "status" : -1 })
            if not order:
                return self.json(message("order is None", 404))
        except:
            return self.json(message("invalid id"))

        # 更新订单
        log = order.log
        log.append({ "addon" : datetime.datetime.now(), "desc" : "开始抢购。", "operator" : "系统" })
        db.order.find_one_and_update({ "_id" : ObjectId(id) }, { "$set" : { "status" : 1, "log" : log } })
        return self.json(message(0, "success"))


@url("/api/account")
class ApiAccount(HandlerBase):

    '''
        hashlib.md5(src).hexdigest().upper()
        获取账号
            1,  校验: sign :  md5(年月日+caonima)
    '''

    def code(self):
        date = time.strftime('%Y%m%d',time.localtime())
        return md5(date)

    def get(self):
        sign = self.get_argument("sign", "")

        code = self.code()
        if code != sign:
            return self.json(message("invalid sign"))
        try:
            result = []
            accounts = db.account.find({ "status" : 1 })
            if accounts.count() > 0:
                for i in accounts:
                    result.append({ "account" : i.account, "password" : i.password })

            return self.json(message("success", 0, result))
        except:
            return self.json(message("error system"))


# @url("/api/finished")
# class ApiFinished(HandlerBase):

#     '''
#         hashlib.md5(src).hexdigest().upper()
#         获取账号
#             1,  校验: sign :  md5(年月日+caonima)
#     '''

#     def code(self, id):
#         date = time.strftime('%Y%m%d',time.localtime())
#         st = "{0}{1}caonima".format(date, id)

#         result = md5(st)

#         return result

#     def post(self):
#         id = self.get_argument("id", "") or None
#         sign = self.get_argument("sign", "")

#         code = self.code(id)
#         if code != sign:
#             return self.json({"status": "faild", "desc": "error sign"})

#         try:
#             order = db.order.find_one({ "_id" : ObjectId(id), "status" : -1 })
#             if not order:
#                 return self.json({"status": "faild", "desc": "invalid id"})
#         except:
#             return self.json({"status": "faild", "desc": "invalid id"})

#         db.order.find_one_and_update({ "_id" : ObjectId(id) }, { "$set" : { "status" : 1 } })
#         return self.json({"status": "ok", "desc": "success"})