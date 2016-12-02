#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# Author: cuckoo
# Email: 454045250@qq.com
# Create Date: 2016-11-29


import json
import datetime
import tornado.web
from bson import ObjectId
from core.web import HandlerBase
from framework.web import paging
from framework.mvc.web import url, get_url
from framework.data.mongo import db, Document, DBRef


@url("/order")
class Order(HandlerBase):

    def where(self, status, key):
        where = {}
        if status != "0":
            where["status"] = int(status)
        if key:
            where["productId"] = {"$regex" : key}

        return where

    def get(self):
        status = self.get_argument("status", "0")
        key = self.get_argument("key", "")

        self.context.status = status
        self.context.key = key

        where = self.where(status, key)
        self.context.orders = db.order.find(where) \
            .skip(paging.skip(self.context.paging)) \
            .limit(self.context.paging.size)
        self.context.paging.count = self.context.orders.count()

        return self.template()


@url("/orderinfo")
class Orderinfo(HandlerBase):

    def get(self):
        id = self.get_argument("id", "") or None
        order = db.order.find_one({ "_id" : ObjectId(id) })

        self.context.order = order
        return self.template()