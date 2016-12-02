#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# Author: hongyi
# Email: hongyi@hewoyi.com.cn
# Create Date: 2016-1-6

import re
import os
import pymongo
import datetime
import tornado.web
from bson import ObjectId
from core.web import HandlerBase
from framework.web import paging
from framework.mvc.web import url
from framework.data.mongo import db, DBRef, Document


@url("/systemlog")
class SystemLog(HandlerBase):
    @tornado.web.authenticated
    def get(self):
        starttime = self.get_argument("starttime", "")
        endtime = self.get_argument("endtime", "")
        key = self.get_argument("key", "")
        logtype = self.get_argument("logtype", "-1")
        receiver = self.get_argument("receiver", "-1")

        self.context.starttime = starttime
        self.context.endtime = endtime
        self.context.key = key
        self.context.logtype = logtype
        self.context.receiver = receiver
        self.context.users = db.user.find()

        where = find_where(starttime, endtime, key, logtype, receiver)
        systemlog = db.systemlog.find(where)

        self.context.systemlog = systemlog.sort([ ("createtime", -1) ]) \
            .skip(paging.skip(self.context.paging)) \
            .limit(self.context.paging.size)
        self.context.paging = paging.parse(self)
        self.context.paging.count = self.context.systemlog.count()

        return self.template()


def find_where(starttime="", endtime="", key="", logtype="-1", receiver="-1"):
    try:
        where = {}
        select_time = {}
        if starttime:
            select_time["$gt"] = datetime.datetime.strptime(starttime + " 00:00:00", "%Y-%m-%d %H:%M:%S")

        if endtime:
            select_time["$lt"] = datetime.datetime.strptime(endtime + " 23:59:59", "%Y-%m-%d %H:%M:%S")

        if select_time:
            where["createtime"] = select_time

        if logtype == "-1":
            where["logtype"] = {"$nin" : [0]}
        else:
            where["logtype"] = int(logtype)

        if key:
            where["operation"] = {"$regex" : key}

        if receiver != "-1" :
            where["user.$id"] = ObjectId(receiver)

    except Exception, e:
        print e
        where = []

    return where
