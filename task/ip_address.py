#!/usr/bin/env python
# -*- encoding:utf-8 -*-


import os
import sys
sys.path.append(os.path.abspath("../"))
reload(sys)
sys.setdefaultencoding('utf-8')

import json
import time
import pymongo
import datetime
import requests
import schedule
from bson import ObjectId
from framework.data.mongo import db, Document, DBRef


def getIpInfo(ip):
    url = "http://api.ip138.com/query/?ip={0}&token=894d33dfaa2f3e2607feea44fa714b20".format(ip)
    try:
        # import pdb
        # pdb.set_trace()
        r = requests.get(url, timeout=5)
        result = json.loads(r.text)
        print result
        if result['ret'] == "ok":
            data = result['data']
            if len(data) == 6:
                ipinfo = "{0}{1}{2}{3}".format(data[0], data[1], data[2], data[3])
            else:
                ipinfo = "%s(未知)" % (ip)
    except Exception, e:
        print e
        ipinfo = "%s(未知)" % (ip)
    return ipinfo

def job():
    try:
        starttime = datetime.datetime(2016,11,11)
        logs = db.systemlog.find({ "status" : {"$exists" : False}, "createtime" : {"$gt" : starttime}})
        print logs.count()
        for i in logs:
            ip = i.ip
            result = "::1" in ip and "::1(本地)" or getIpInfo(ip)
            db.systemlog.find_one_and_update({ "_id" : i._id }, {"$set" : { "ip" : result, "status" : True } })

    except Exception as e:
        print e


if __name__ == "__main__":
    schedule.every(1).seconds.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)