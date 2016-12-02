#!/usr/bin/env python
# -*- encoding:utf-8 -*-
# Author: lixingtie
# Email: 260031207@qq.com
# Create Date: 2014-8-11


import json
import datetime
import requests
from bson import ObjectId
from framework.web import paging
from framework.mvc.web import RequestHandler
from framework.data.mongo import db, Document, DBRef

try:
    from personal import CUSTOMER
except Exception, e:
    try:
        from settings import CUSTOMER
    except Exception, e:
        CUSTOMER = ""

try:
    from personal import PROJECT_NAME
except Exception, e:
    try:
        from settings import PROJECT_NAME
    except Exception, e:
        PROJECT_NAME = None


class HandlerBase(RequestHandler):
    """
        页面处理器基类
        1. 显示当前用户
        2. 引用全局分页语句
        3. 读取当前用户权限
    """

    def initialize(self):
        current_user = db.user.find_one({"_id": ObjectId(self.get_current_user())})
        self.context.current_user = current_user
        self.context.paging = paging.parse(self)

    def get_current_user(self):
        user = db.user.find_one({'_id': ObjectId(self.get_secure_cookie("u"))})
        return self.get_secure_cookie("u")

    def json(self, obj, content_type="text/json; charset=utf-8", cls=None):
        """
            输出json结果
        """
        self.set_header("Content-Type", content_type)
        self.write(json.dumps(obj, cls=cls).replace("</", "<\\/"))

    def system_record(self, user, logtype, operation, content):
        """
            搜集系统异常并写入系统日志
            字段:
                用户(DBRef/管理员/系统)
                类型 -1(系统错误) 1(登陆记录) 2(预约) 3(归属地查询) 4(IP查询) 5(数据更新)
                模块
                操作
                内容
                时间 
                IP
        """
        if user not in ["管理员", "系统"]:
            user = DBRef("user", user)

        path = self.get_template_name()
        ip = self.request.remote_ip

        log = Document()
        log.user = user
        log.logtype = logtype
        log.module = "templates/" in path and path.split("templates/")[1] or path
        log.operation = operation
        log.content = content
        log.createtime = datetime.datetime.now()
        log.ip = ip

        db.systemlog.save(log)
