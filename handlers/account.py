#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# Author: cuckoo
# Email: 454045250@qq.com
# Create Date: 2016-11-29

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
            account.site = 'yongle'
            account.status = int(status)

            db.account.save(account)

            return self.json({"status": "ok"})
        except Exception, e:
            print e
            return self.json({"status": "faild", "desc": "未知错误!"})


@url("/account/import")
class AccountImport(HandlerBase):

    def post(self):
        try:
            file_metas=self.request.files['file']
            file_name = "filename" in file_metas[0] and file_metas[0]["filename"] or "error file"
            if ".txt" not in file_name:
                return self.write("未选择文件或文件格式错误!")
        except Exception, e:
            return self.write("未选择文件或文件格式错误!")

        for meta in file_metas:
            try:
                # 按行分割字符串
                body_list = meta['body'].split('\n')
                # 得到元素列表
                element = [ i.split("----") for i in body_list ]

                lines = []

                for i in element:
                    account = i[0]
                    password = i[1]

                    if db.account.find_one({ "account" :account }):
                        lines.append("重复的账号: {0}\n\r".format(account))
                    else:
                        lines.append("成功的账号: {0}\n\r".format(account))
                        db.account.insert_one({ "account" : account, "password" : password, \
                            "status" : 1, "created" : datetime.datetime.now()})

                for l in lines:
                    self.write(l)
            except Exception, e:
                print e
                return self.write("未知错误!")
        # self.context.ps = '11'
        # return self.template()
