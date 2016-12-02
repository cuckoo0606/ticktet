#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# Author: cuckoo
# Email: 454045250@qq.com
# Create Date: 2016-11-29

import os
import tornado.web
from core.web import HandlerBase
from framework.web import paging
from framework.mvc.web import url
from framework.data.mongo import db
from bson import ObjectId
import re


@url("/")
class Index(HandlerBase):
    def get(self):
        return self.redirect("/home")
