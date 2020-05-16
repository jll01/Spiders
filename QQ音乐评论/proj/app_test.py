#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   app_test.py
# @Time    :   2019/9/16 16:11
# @Author  :   LJL
# @Version :   1.0
# @Email   :   491692391@qq.com
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


from celery import Celery

app = Celery('proj', include=['proj.tasks'])
app.config_from_object('proj.celeryconfig')

if __name__ == '__main__':
    app.start()