#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# Author: hongyi
# Email: hongyi@hewoyi.com.cn
# Create Date: 2016-1-25

import os
import re
import datetime
import requests
import tornado.web
from bson import ObjectId
from core.web import HandlerBase
from framework.web import paging
from framework.mvc.web import url, get_url
from framework.data.mongo import db, Document, DBRef


@url("/acts")
class NewsIssue(HandlerBase):

    @tornado.web.authenticated
    def get(self):


        key = self.get_argument("key", "")
        self.context.key = key

        where = {}
        if key:
            where["$or"] = [{"title": {"$regex": key}},
                            {"content": {"$regex": key}}]

        self.context.paging = paging.parse(self)
        self.context.news = db.news.find(where) \
            .skip(paging.skip(self.context.paging)) \
            .limit(self.context.paging.size)
        self.context.paging.count = self.context.news.count()

        return self.template()

