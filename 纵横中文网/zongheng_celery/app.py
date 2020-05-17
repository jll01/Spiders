#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   app.py
# @Time    :   2020/4/26 16:11
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


from celery import Celery

app = Celery('zongheng_celery', include=['zongheng_celery.tasks'])
app.config_from_object('zongheng_celery.config')


if __name__ == '__main__':
    app.start()
