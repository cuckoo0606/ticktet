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
                
                # 更改状态
                log = order.log
                log.append({ "addon" : datetime.datetime.now(), "desc" : "开始抢购。", "operator" : "系统" })
                db.order.find_one_and_update({ "_id" : order._id }, { "$set" : { "status" : 1, "log" : log } })
                return self.json(message("success", 0, result))
            else:
                return self.json(message("order is None", 404))
        except:
            return self.json(message("error system"))


@url("/api/update")
class ApiUpdate(HandlerBase):

    '''
        hashlib.md5(src).hexdigest()
        更新订单状态: 执行 >> 成功
            1,  状态 1 >> 2, 添加log
            2,  校验: sign :  md5(年月日+id)
            3,  接收: 账号, 订单id, 金额, 数量
    '''

    def code(self):
        date = time.strftime('%Y%m%d',time.localtime())

        return md5(date)

    def post(self):
        body = tornado.escape.json_decode(self.request.body)
        sign = 'sign' in body and  body['sign'] or ''
        status = 'status' in body and body['status']
        msg = 'msg' in body and body['msg'] or ''
        id = 'id' in body and body['id'] or None
        data = 'data' in body and body['data'] or {}

        code = self.code()
        if code != sign:
            return self.json(message("invalid sign"))
        try:
            order = db.order.find_one({ "_id" : ObjectId(id) })
            if not order:
                return self.json(message("order is None", 404))
        except:
            return self.json(message("invalid id"))

        # 更新订单
        desc = {}
        account = 'account' in data and data['account'] or '未知'
        password = 'password' in data and data['password'] or '未知'
        price = 'price' in data and data['price'] or '未知'
        count = 'count' in data and data['count'] or '未知'

        desc = "抢购{0}, 账号:{1}, 密码:{2}, 总金额{3}元, 总{4}张.({5})".format(status==0 and '成功' or '失败', \
                account, password, price, count, msg)
        
        log = order.log
        log.append({ "addon" : datetime.datetime.now(), "desc" : desc, "operator" : "系统" })
        db.order.find_one_and_update({ "_id" : ObjectId(id) }, { "$set" : { "log" : log } })
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
        site = self.get_argument("site", "")

        code = self.code()
        if code != sign:
            return self.json(message("invalid sign"))
        if not site:
            return self.json(message("invalid site"))
        try:
            result = []
            accounts = db.account.find({ "status" : 1, "site" : site })
            if accounts.count() > 0:
                for i in accounts:
                    result.append({ "account" : i.account, "password" : i.password, 'site' : i.site })

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
