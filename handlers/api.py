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


@url("/api/task")
class ApiTask(HandlerBase):

    '''
        获取订单
            1,  status : -1
            2,  site : [yongle, damai]
            3,  时间判断
            4,  校验: verify :  md5(年月日+类型+caonima)
    '''

    def code(self, site):
        date = time.strftime('%Y%m%d',time.localtime())
        st = "{0}{1}caonima".format(date, site)

        result = md5(st)

        return result

    def get(self):
        site = self.get_argument("site", "yongle")
        verify = self.get_argument("verify", "")

        if not verify:
            return self.json({"status": "faild", "desc": "not verify!"})

        if site not in [ "yongle" ]:
            return self.json({"status": "faild", "desc": "invalid site"})

        code = self.code(site)

        if code != verify:
            return self.json({"status": "faild", "desc": "error verify"})

        now = datetime.datetime.now()

        try:
            where = {}
            where['status'] = -1
            where['site'] = site
            where['starttime'] = { "$lte" : now }
            where['endtime'] = { "$gte" : now }

            order = db.order.find_one(where)

            if order:
                result = Document()
                result.id = str(order._id)
                result.count = str(order.count)
                result.productId = order.productId
                result.productPlayIds = order.productPlayIds
                result.maxprice = order.maxprice
                result.minprice = order.minprice

                return self.json({"status": "ok", "desc": result})
            else:
                return self.json({"status": "faild", "desc": "nothing"})

        except:
            return self.json({"status": "faild", "desc": "system error"})


@url("/api/update")
class ApiUpdate(HandlerBase):

    '''
        hashlib.md5(src).hexdigest().upper()
        更新订单状态
            1,  状态 -1 >> 1, 添加log
            2,  校验: verify :  md5(年月日+id+caonima)
    '''

    def code(self, id):
        date = time.strftime('%Y%m%d',time.localtime())
        st = "{0}{1}caonima".format(date, id)

        result = md5(st)

        return result

    def post(self):
        id = self.get_argument("id", "") or None
        verify = self.get_argument("verify", "")

        code = self.code(id)
        if code != verify:
            return self.json({"status": "faild", "desc": "error verify"})

        try:
            order = db.order.find_one({ "_id" : ObjectId(id), "status" : -1 })
            if not order:
                return self.json({"status": "faild", "desc": "invalid id"})
        except:
            return self.json({"status": "faild", "desc": "invalid id"})

        db.order.find_one_and_update({ "_id" : ObjectId(id) }, { "$set" : { "status" : 1 } })
        return self.json({"status": "ok", "desc": "success"})


@url("/api/account")
class ApiAccount(HandlerBase):

    '''
        hashlib.md5(src).hexdigest().upper()
        获取账号
            1,  校验: verify :  md5(年月日+caonima)
    '''

    def code(self):
        date = time.strftime('%Y%m%d',time.localtime())
        st = "{0}caonima".format(date)

        result = md5(st)

        return result

    def get(self):
        verify = self.get_argument("verify", "")

        code = self.code()
        if code != verify:
            return self.json({"status": "faild", "desc": "error verify"})

        try:
            result = []
            accounts = db.account.find({ "status" : 1 })
            if accounts.count() > 0:
                for i in accounts:
                    result.append({ "account" : i.account, "password" : i.password })

            return self.json({"status": "ok", "desc": result})
        except:
            return self.json({"status": "faild", "desc": "system error"})


# @url("/api/finished")
# class ApiFinished(HandlerBase):

#     '''
#         hashlib.md5(src).hexdigest().upper()
#         获取账号
#             1,  校验: verify :  md5(年月日+caonima)
#     '''

#     def code(self, id):
#         date = time.strftime('%Y%m%d',time.localtime())
#         st = "{0}{1}caonima".format(date, id)

#         result = md5(st)

#         return result

#     def post(self):
#         id = self.get_argument("id", "") or None
#         verify = self.get_argument("verify", "")

#         code = self.code(id)
#         if code != verify:
#             return self.json({"status": "faild", "desc": "error verify"})

#         try:
#             order = db.order.find_one({ "_id" : ObjectId(id), "status" : -1 })
#             if not order:
#                 return self.json({"status": "faild", "desc": "invalid id"})
#         except:
#             return self.json({"status": "faild", "desc": "invalid id"})

#         db.order.find_one_and_update({ "_id" : ObjectId(id) }, { "$set" : { "status" : 1 } })
#         return self.json({"status": "ok", "desc": "success"})