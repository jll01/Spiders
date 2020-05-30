#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   duanzi.py
# @Time    :   2019/10/8 16:33
# @Author  :   LJL
# @Version :   1.0
# @Email   :   491692391@qq.com
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


from celery_template.tasks import get_content


class Comment(object):
    def __init__(self, page_num):
        self.page_num = page_num

    def main(self):
        get_content(self.page_num)


if __name__ == '__main__':
    page_num = 50

    comment = Comment(page_num)
    comment.main()
