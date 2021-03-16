import json
import hashlib
import logging
import os
import socket

from datetime import datetime
from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import api_settings as settings
import icp_requests


app = Flask(__name__)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200/day", "50/hour", "1/5seconds"],
)


def judge(in_func_name):
    """
    判断是否开启了限制访问
    @param in_func_name: 请求的方法名
    @return: 是的话返回限制的方法，否则不限制
    """
    if settings.IS_LIMIT:
        if in_func_name == 'get_current_icp_nation':
            limit_func = limiter.limit(settings.LIMIT_ICP_NATION)
        else:
            limit_func = limiter.limit('1/3seconds', override_defaults=False)
    else:
        limit_func = limiter.exempt
    return limit_func


# 访问频率过快的时候返回
@app.errorhandler(429)
def ratelimit_handler(e):
    logger_ret.debug(f'ip: {request.remote_addr} - api: {request.path} - requests speed is too fast')
    return json.dumps({"code": 0, "msg": "访问速度过快, 请稍后再试！", "result": {}}, ensure_ascii=False)


# 只接受POST方法访问，获取网站icp和备案公司名称,国家网站
@app.route("/api_get_icp_nation", methods=["POST"])
@judge('get_current_icp_nation')
def get_current_icp_nation():
    # 默认返回内容
    # 获取传入的参数
    get_data = json.loads(request.get_data())
    num, return_con = judge_par(get_data, ['index_url'])
    if not num:
        return return_con
    # 获取
    index_url = get_data.get('index_url')
    info = icp_requests.main(index_url)
    # # 对参数进行操作
    return json.dumps(info, ensure_ascii=False)


def judge_par(get_data, par):
    """
    判断传入的参数是否正确
    @param get_data: 请求的参数
    @param par: 需要判断的参数
    @return: 判断后的返回的信息
    """
    # token值
    now = datetime.today()
    token = hashlib.md5(f'spider_{now.year}-{now.month}-{now.day}'.encode('utf-8')).hexdigest()
    # 是否有参数
    if not get_data:
        return_dict = {"code": 0, "msg": "请检查参数", "result": {}}
        logger_ret.debug(f'ip: {request.remote_addr} - api: {request.path} - request parameter: {get_data} - return: {return_dict}')
        return 0, json.dumps(return_dict, ensure_ascii=False)

    # 判断token值
    if get_data.get('token', '') != token:
        return_dict = {"code": 0, "msg": "token错误", "result": {}}
        logger_ret.debug(f'ip: {request.remote_addr} - api: {request.path} - request parameter: {get_data} - return: {return_dict}')
        return 0, json.dumps(return_dict, ensure_ascii=False)

    # 请求必须的参数
    for i in par:
        if not get_data.get(i, ''):
            return_dict = {"code": 0, "msg": "请求参数错误", "result": {}}
            # 保存日志
            logger_ret.debug(f'ip: {request.remote_addr} - api: {request.path} - request parameter: {get_data} - return: {return_dict}')
            return 0, json.dumps(return_dict, ensure_ascii=False)

    return 1, ''


def get_logger(log_path, logfile_name):
    """
    保存不同的日志级别到不同的文件里面
    @param log_path: 路径
    @param logfile_name: 文件名
    @return: 日志队形
    """
    logging_format = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(lineno)s - %(message)s')
    log_files = {
        logging.DEBUG: os.path.join(log_path, logfile_name + '_debug.log'),
        # logging.INFO: os.path.join(log_path, logfile_name + '_info.log'),
        # logging.WARNING: os.path.join(log_path, logfile_name + '_warning.log'),
        # logging.ERROR: os.path.join(log_path, logfile_name + '_error.log'),
        # # 严重错误信息，系统崩溃
        # logging.CRITICAL: os.path.join(log_path, logfile_name + '_critical.log')
    }
    # 和flask默认使用同一个logger
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    for log_level, log_file in log_files.items():
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging_format)
        logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.name = "console"
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging_format)
    logger.addHandler(console_handler)
    return logger


if __name__ == "__main__":
    # get_logger(日志保存路径，日志文件名)
    logger_ret = get_logger('./flasklog', 'flask_api_log')
    app.run(host=f'{socket.gethostbyname(socket.gethostname())}', port=8000, debug=True)
