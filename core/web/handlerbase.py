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

    def write_error(self, status_code, **kwargs):
        if status_code in [401, 403, 404, 500, 503]:
            kwargs["message"] = status_code
            self.render("error/401.html", **kwargs)
        else:
            self.write("BOOM!")

    def get_lower_user(self):
        """
            获取当前用户自己和自己的下级
        """
        current_user = self.context.current_user
        c_role = current_user.userrole.fetch().roleid

        if c_role == "admin":
            reg = "^/admin"
        else:
            reg = "^%s" % current_user.relation

        return reg

    def get_lower_notuser(self):
        """
            获取当前用户的下级
        """
        current_user = self.context.current_user
        c_role = current_user.userrole.fetch().roleid

        if c_role == "admin":
            reg_user = "^/admin/"
        else:
            reg_user = "^%s/" % current_user.relation

        return reg_user

    def system_record(self, user, logtype, operation, content):
        """
            搜集系统异常并写入系统日志
            字段:
                用户(DBRef/管理员/系统)
                类型 0(系统错误) 1(登陆记录) 2(资金变动) 3(用户操作[增删改]) 99(资金调整)
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


def find_parents(user, parents):
    """
        查询非管理员的上级
    """
    if user and user.parent:
        try:
            parent = user.parent.fetch()
            if parent and parent.userrole.fetch().roleid != "admin":
                parents.append(parent)
                find_parents(parent, parents)
        except Exception as e:
            print e
            return []
    return parents
