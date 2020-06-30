#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   app.py
# @Time    :   2020/6/12 10:11
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


from celery import Celery

app = Celery('celery_template', include=['celery_template.tasks'])
app.config_from_object('celery_template.config')


if __name__ == '__main__':
    app.start()
