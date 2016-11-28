#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# Author: hongyi
# Email: hongyi@hewoyi.com.cn
# Create Date: 2016-1-25

import datetime
import tornado.web
from bson import ObjectId
from core.web import HandlerBase
from framework.web import paging
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


@url("/order/edit")
class OrderEdit(HandlerBase):

    @tornado.web.authenticated
    def get(self):
        id = self.get_argument('id', '') or None
        act = db.acts.find_one({ '_id' : ObjectId(id) })
        if not act:
            return self.json({"status": "faild", "desc": "没有此场次!"})

        self.context.act = act

