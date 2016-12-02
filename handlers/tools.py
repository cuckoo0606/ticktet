#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# Author: cuckoo
# Email: 454045250@qq.com
# Create Date: 2016-11-29


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


@url("/ip")
class IP(HandlerBase):

    def get(self):


        return self.template()


@url("/mobile")
class Mobile(HandlerBase):

    def get(self):
        id = self.get_argument("id", "")
        result = self.get_argument("result", "")


        # reg = r"^(13[0-9]|15[012356789]|17[0123678]|18[0-9]|14[57])[0-9]{8}$"
        # if not re.match(reg, mobile):
        #     return self.json({"status": "faild", "desc": "手机号码格式不正确!"})
        

        self.context.id = id
        self.context.result = 1

        return self.template()

    def post(self):

        id = self.get_argument("id", "")
        result = "结果是: {0}".format(id)
        print result


        self.context.id = id
        self.context.result = result

        return self.template()