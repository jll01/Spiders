#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   zongheng_celery_run.py
# @Time    :   2020/4/14 16:44
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


from zongheng_celery.tasks import get_content


class Comment(object):
    def __init__(self, page_num):
        self.page_num = page_num

    def main(self):
        get_content(self.page_num)


if __name__ == '__main__':
    page_num = 2

    comment = Comment(page_num)
    comment.main()
