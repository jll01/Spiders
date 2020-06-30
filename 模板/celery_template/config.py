#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   config.py
# @Time    :   2020/6/12 10:12
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


BROKER_URL = 'redis://192.168.1.102:6379/0'  # 使用Redis作为消息代理
CELERY_RESULT_BACKEND = 'redis://192.168.1.102:6379/3' # 把任务结果存在了Redis
CELERY_TASK_SERIALIZER = 'msgpack'  # 任务序列化和反序列化使用msgpack方案
CELERY_RESULT_SERIALIZER = 'json'  # 读取任务结果一般性能要求不高，所以使用了可读性更好的JSON
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24  # 任务过期时间
CELERY_ACCEPT_CONTENT = ['json', 'msgpack']  # 指定接受的内容类型

# # 任务发送完成是否需要确认，这一项对性能有一点影响
# CELERY_ACKS_LATE = True
# # 压缩方案选择，可以是zlib, bzip2，默认是发送没有压缩的数据
# CELERY_MESSAGE_COMPRESSION = 'zlib'
# # 规定完成任务的时间
# CELERYD_TASK_TIME_LIMIT = 5  # 在5s内完成任务，否则执行该任务的worker将被杀死，任务移交给父进程
# # celery worker的并发数，默认是服务器的内核数目,也是命令行-c参数指定的数目
# CELERYD_CONCURRENCY = 4
# # celery worker 每次去rabbitmq预取任务的数量
# CELERYD_PREFETCH_MULTIPLIER = 4
# # 每个worker执行了多少任务就会死掉，默认是无限的
# CELERYD_MAX_TASKS_PER_CHILD = 40
# 设置默认的队列名称，如果一个消息不符合其他的队列就会放在默认队列里面，如果什么都不设置的话，数据都会发送到默认的队列中
# CELERY_DEFAULT_QUEUE = "default"
# # 设置详细的队列
# CELERY_QUEUES = {
#     "default": { # 这是上面指定的默认队列
#         "exchange": "default",
#         "exchange_type": "direct",
#         "routing_key": "default"
#     },
#     "topicqueue": { # 这是一个topic队列 凡是topictest开头的routing key都会被放到这个队列
#         "routing_key": "topic.#",
#         "exchange": "topic_exchange",
#         "exchange_type": "topic",
#     },
#     "task_eeg": { # 设置扇形交换机
#         "exchange": "tasks",
#         "exchange_type": "fanout",
#         "binding_key": "tasks",
#     },
# }