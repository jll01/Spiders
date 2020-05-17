#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   celeryconfig.py
# @Time    :   2020/3/1 16:12
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


BROKER_URL = 'redis://192.168.1.103:6379/3' # 使用Redis作为消息代理

# CELERY_RESULT_BACKEND = 'redis://localhost:6379/4' # 把任务结果存在了Redis

CELERY_TASK_SERIALIZER = 'msgpack' # 任务序列化和反序列化使用msgpack方案

CELERY_RESULT_SERIALIZER = 'json' # 读取任务结果一般性能要求不高，所以使用了可读性更好的JSON

CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24 # 任务过期时间

CELERY_ACCEPT_CONTENT = ['json', 'msgpack'] # 指定接受的内容类型


# ELERY_IMPORTS = ('tasks')
# CELERY_IGNORE_RESULT = False
# BROKER_HOST = '127.0.0.1'
# BROKER_PORT = 5672
# BROKER_URL = 'amqp://'
# #CELERY_RESULT_BACKEND = 'amqp'
# CELERY_RESULT_BACKEND = 'mongodb'
# CELERY_RESULT_BACKEND_SETTINGS = {
#         "host":"127.0.0.1",
#         "port":27017,
#         "database":"jobs",
#         "taskmeta_collection":"stock_taskmeta_collection",
# }