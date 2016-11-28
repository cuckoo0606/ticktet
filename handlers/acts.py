#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# Author: hongyi
# Email: hongyi@hewoyi.com.cn
# Create Date: 2016-1-25


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

# import os
# import sys
# sys.path.append(os.path.abspath("../"))
# reload(sys)
# sys.setdefaultencoding('utf-8')
# from task import auto_acts

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

    @tornado.web.authenticated
    def get(self):
        id = self.get_argument('id', '') or None
        act = db.acts.find_one({ '_id' : ObjectId(id) })

        try:
            self.context.act = act
            self.context.price = act.price
        except Exception, e:
            print e

        return self.template()


@url("/acts/update")
class ActsUpdate(HandlerBase):
    def post(self):
        try:
            hand_acts.check_acts()
            return self.json({"status": "ok"})
        except:
            return self.json({"status": "faild", "desc": "刷新失败!"})
        pass