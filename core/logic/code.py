#!/usr/bin/env python
# -*- encoding:utf-8 -*-


import os
import sys
sys.path.append(os.path.abspath("../../"))
# reload(sys)
# sys.setdefaultencoding('utf-8')

import json
import random
import requests
import datetime
from framework.data.mongo import db

try:
    from personal import CODE_ACCOUNT, CODE_PASSWORD
except Exception, e:
    try:
        from settings import CODE_ACCOUNT, CODE_PASSWORD
    except Exception, e:
        CODE_ACCOUNT = ""
        CODE_PASSWORD = ""

try:
    from personal import CODE_TYPE
except Exception, e:
    try:
        from settings import CODE_TYPE
    except Exception, e:
        CODE_TYPE = -1


class PhoneCode(object):

    def getcode(self, phone):
        """
            发送验证码
            返回码: "2":成功, "406":手机号码格式错误, "-1":系统错误, 其他:其他错误
        """
        code = "{0}{1}{2}{3}".format(random.randint(0, 9), random.randint(0, 9), random.randint(0, 9), random.randint(0, 9))

        url_head = "https://106.ihuyi.com/webservice/sms.php?method=Submit&account="

        # 百亿正式用户
        if CODE_TYPE == 1:
            url_content = "{0}&password={1}&mobile={2}&content=您的验证码是：【{3}】。请不要把验证码泄露给其他人。".format(\
                    CODE_ACCOUNT, CODE_PASSWORD, phone, code)
        else:
            url_content = "{0}&password={1}&mobile={2}&content=您的验证码是：{3}。请不要把验证码泄露给其他人。".format(\
                    CODE_ACCOUNT, CODE_PASSWORD, phone, code)

        url = url_head + url_content
        try:
            r = requests.get(url, timeout=5)
            r.encoding = 'utf-8'
            status = r.text.split("<code>")[1].split("</code>")[0]
        except Exception, e:
            db.baiyierror.insert_one({
                "url" : "getcode",
                "phone" : phone,
                "created" : datetime.datetime.now() 

            })
            status = "-1"

        result = {"code" : code, "status" : status}

        return result


    def sendinfo(self, phone, userid, pwd):
        '''
            恭喜您注册成功，您的账号是【变量】，密码是【变量】，请牢记。
        '''
        url_head = "https://106.ihuyi.com/webservice/sms.php?method=Submit&account="
        url_content = "{0}&password={1}&mobile={2}&content=恭喜您注册成功，您的账号是【{3}】，密码是【{4}】，请牢记。".format(
            CODE_ACCOUNT, CODE_PASSWORD, phone, userid, pwd)

        url = url_head + url_content
        try:
            r = requests.get(url, timeout=5)
            # r.encoding = 'utf-8'
            # status = r.text.split("<code>")[1].split("</code>")[0]
            # print status
        except Exception, e:
            db.baiyierror.insert_one({
                "url" : "sendinfo",
                "phone" : phone,
                "userid" : userid,
                "created" : datetime.datetime.now() 

            })
            print e


if __name__ == "__main__":
    phone = "13929198406"

    app = PhoneCode()
    code = app.getcode(phone)