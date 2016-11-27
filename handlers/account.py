#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# Author: hongyi
# Email: hongyi@hewoyi.com.cn
# Create Date: 2016-1-25

import os
import re
import tornado.web
import time
import datetime
from bson import ObjectId
from core.web import HandlerBase
from framework.web import paging
from framework.mvc.web import url
from framework.data.mongo.escape import BSONEncoder
from framework.data.mongo import db, Document, DBRef


@url("/account/check")
class AccountCheck(HandlerBase):

    def get(self):
        account_id = self.get_argument('account_id', '0')
        where = {}
        if account_id != '0':
            where['_id'] = ObjectId(account_id)
        
        account = db.account.find(where)
        accounts = db.account.find()

        self.context.account = account
        self.context.accounts = accounts
        self.context.account_id = account_id

        return self.template()


@url("/account/edit")
class AccountEdit(HandlerBase):

    def get(self):
        id = self.get_argument('id', '') or None
        account = db.account.find_one({ '_id' : ObjectId(id) })

        self.context.account = account

        return self.template()


    def post(self):
        id = self.get_argument("id", "") or None
        accountid = self.get_argument("account", "")
        password = self.get_argument("password", "")
        status = self.get_argument("status", 1)

        if not accountid or not password or not status or not status:
            return self.json({"status": "faild", "desc": "参数不齐全!"})
        try:
            if id:
                account = db.account.find_one({ '_id' : ObjectId(id) })
            else:
                account = Document()

                account.created = datetime.datetime.now()

            account.account = accountid
            account.password = password
            account.status = int(status)

            db.account.save(account)

            return self.json({"status": "ok"})
        except Exception, e:
            print e
            return self.json({"status": "faild", "desc": "未知错误!"})
