#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   save_item.py
# @Time    :   2019/11/2 12:23
# @Author  :   LJL
# @Version :   1.0
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib


import pymysql
import redis
import pymongo
import time
import sys

from threading import Lock


def mysql_connect(host='localhost', port=3306, user='root', password='0000', db='scrapytest'):
    """
    连接mysql数据库，返回连接和游标对象
    :param host: 主机ip， 默认本地主机
    :param port: mysql在本地的端口号， 默认为3306
    :param user: 连接MySQL的用户，默认root
    :param password: user的密码
    :param db: 接的数据库名
    :return: 连接和游标对象
    """
    # try:
    connect = pymysql.connect(host=host, user=user, port=port, password=password, db=db)
    cur = connect.cursor()
    return connect, cur
    # except Exception as err:
    #     print('连接出错！{}'.format(err))
    #     return 0, 0


def with_save_data(inner):
    def func_in(connect, cur, table_name, item, lock=None):
        """
        装饰器, 通过判断传入的lock参数确认是否是多线程存储数据，是的话需要线程锁才能存储数据
        :param connect: 数据库连接对象
        :param cur: 数据库连接游标对象
        :param table_name: mysql数据库中保存数据的表名称
        :param item: 要保存的数据(字典格式)
        :param lock: 线程锁,是否是多线程，多线程存储数据的话要开启线程锁
        :return:
        """
        if type(lock) == type(Lock()):
            lock.acquire()
            inner(connect, cur, table_name, item, lock=None)
            lock.release()
        else:
            inner(connect, cur, table_name, item, lock=None)
    return func_in


@with_save_data
def mysql_save_data(connect, cur, table_name, item, lock=None):
    """
    将数据保存到mysql中,
    :param connect: 数据库连接对象
    :param cur: 数据库连接游标对象
    :param table_name: mysql数据库中保存数据的表名称
    :param item: 要保存的数据(字典格式)
    :param lock: 线程锁,是否是多线程，多线程存储数据的话要开启线程锁
    :return:
    """
    try:
        if not isinstance(item, dict):
            print('数据格式错误！要求格式为dict,请检查格式后重试')
            sys.exit()
        else:
            try:
                db_value = tuple(item.values())
                db_field = str(tuple(item.keys())).replace("'", '')
                cur.execute('''insert into {} {} values {}'''.format(table_name, db_field, db_value))
                connect.commit()
            except pymysql.err.ProgrammingError:
                print("""表%s不存在！""" % table_name)
                sys.exit()
            except Exception as err:
                print('数据出错：{}'.format(err))
            else:
                print('{}保存成功!'.format(item))
    except:
        sys.exit()


def redis_connect(host='localhost', port=6379, db=0):
    """
    使用redis连接池创建连接对象
    :param host: 主机ip, 默认本地主机
    :param port: 本地redis数据库连接端口号,默认6379
    :param db: 选择的数据库，默认选择第一个
    :return: 返回连接池对象
    """
    pool = redis.ConnectionPool(host=host, port=port, db=db)
    red = redis.Redis(connection_pool=pool)
    return red


def redis_save_data(connect, item, db_field=int(time.time()*100000)):
    """
    将传入的数据保存到redis数据库中，判断传入的数据item是否是字典类型，不是则退出
    :param connect: 连接对象，在redis_connect()中创建
    :param item: 要保存的数据，字典格式
    :param db_field: 保存在redis中的字典key, 默认是当前的时间戳
    :return: 无
    """
    try:
        # 判断是否是dict类型的数据
        if not isinstance(item, dict):
            print('数据格式错误！要求格式为dict,请检查格式后重试')
            sys.exit()
        else:
            try:
                # 保存数据
                connect.hmset(db_field, item)
            except Exception as err:
                print('数据出错：{}'.format(err))
            else:
                print('{}保存成功!'.format(item))
    except:
        sys.exit()


def mongo_connect(host='localhost', port=27017, db_name='scrapytest', collect='test'):
    """
    mongo数据库连接
    :param host: 主机ip,默认本地主机
    :param port: mongo数据库的端口号, 默认27017
    :param db_name: 连接的数据库名
    :param collect: 保存数据的集合
    :return: 返回已经连接的集合对象
    """
    # 创建连接
    client = pymongo.MongoClient(host=host, port=port)
    # 查询client中的数据库
    dblist = client.list_database_names()
    # 判断数据库python是否存在，不存在则创建
    if db_name not in dblist:
        db = client[db_name]
    else:
        # 连接python数据库
        db = client[db_name]

    # 获取集合名称
    coll_list = db.list_collection_names()
    # 判断集合是否存在，不存在则创建
    if collect not in coll_list:
        coll = db[collect]
    else:
        coll = db[collect]

    return coll


def mongo_save_data(connect, item):
    """
    将数据保存到mongo数据库中
    :param connect: mongo_connect()中连接的集合对象
    :param item: 要保存的数据
    :return:
    """
    try:
        if not isinstance(item, dict):
            print('数据格式错误！要求格式为dict,请检查格式后重试')
            sys.exit()
        else:
            try:
                connect.insert(item)
            except Exception as err:
                print('数据出错：{}'.format(err))
            else:
                print('{}保存成功!'.format(item))
    except:
        sys.exit()
