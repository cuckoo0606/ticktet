#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# Author: cuckoo
# Email: 454045250@qq.com
# Create Date: 2016-11-29

import re
import os
import tornado.web
from bson import ObjectId
from core.web import HandlerBase
from framework.web import paging
from framework.mvc.web import url
from framework.util.html import strip_tags
from framework.data.mongo import db, DBRef


@url("/home")
class Home(HandlerBase):
    @tornado.web.authenticated
    def get(self):
        id = self.get_current_user()

        return self.redirect("/user")
