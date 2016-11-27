#!/usr/lib/env python
#-*- encoding:utf-8 -*-

import random
import datetime
from bson import ObjectId
from pymongo import MongoClient
from framework.data.mongo import db, DBRef, Document
from settings import MONGODB_HOST, MONGODB_PORT, MONGODB_DB, MONGODB_USER, MONGODB_PASSWORD

if __name__ == "__main__":
    # 服务器mongo配置
    # client = MongoClient(MONGODB_HOST, MONGODB_PORT, document_class=Document)[MONGODB_DB]
    # client.authenticate(MONGODB_USER, MONGODB_PASSWORD)

    # db = client

    # 本地mongo配置
    
    user = {}
    user['userid'] = 'admin'
    user['username'] = '管理员'
    user['password'] = '21232f297a57a5a743894a0e4a801fc3'
    user['status'] = 1
    user['created'] = datetime.datetime.now()
    user['score'] = 9999
    user['phone'] = ''

    db.user.insert_one(user)
