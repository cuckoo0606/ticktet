#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# Author: hongyi
# Email: hongyi@hewoyi.com.cn
# Create Date: 2016-1-25


import re
import os
import random
import datetime
import tornado.web

from bson import ObjectId
from core.web import HandlerBase
from framework.web import paging
from framework.mvc.web import url
from framework.util.security import md5
from framework.data.mongo import db, Document, DBRef


@url("/user")
class User(HandlerBase):

    def get(self):
        users = db.user.find()
        user_id = self.get_argument("user_id", "0")

        self.context.users = users
        self.context.user_id = user_id

        where = {}
        if user_id != "0":
            where['_id'] = ObjectId(user_id)
        self.context.user = db.user.find(where).sort([("_id", -1)]) \
            .skip(paging.skip(self.context.paging)) \
            .limit(self.context.paging.size)
        self.context.paging.count = self.context.user.count()

        return self.template()


@url("/user/edit")
class UserEdit(HandlerBase):

    @tornado.web.authenticated
    def get(self):
        id = self.get_argument('id', '') or None
        user = db.user.find_one({ '_id' : ObjectId(id) })

        self.context.user = user

        return self.template()

    @tornado.web.authenticated
    def post(self):
        id = self.get_argument("id", "") or None
        userid = self.get_argument("userid", "")
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        phone = self.get_argument("phone", "")
        status = self.get_argument("status", 1)

        if not userid or not username or not status or not password:
            return self.json({"status": "faild", "desc": "参数不齐全!"})
        try:
            if id:
                user = db.user.find_one({ '_id' : ObjectId(id) })
            else:
                if not password:
                    return self.json({"status": "faild", "desc": "密码不能留空!"})
                if db.user.find_one({ 'userid' : userid }):
                    return self.json({"status": "faild", "desc": "用户ID已存在!"})
                user = Document()
                user.userid = userid
                user.score = 0
                user.created = datetime.datetime.now()

            user.password = md5(password)
            user.username = username
            user.status = int(status)
            user.phone = phone
            db.user.save(user)

            return self.json({"status": "ok"})
        except Exception, e:
            print e
            self.system_record("系统", 0, "添加用户", e.message)
            return self.json({"status": "faild", "desc": "未知错误!"})