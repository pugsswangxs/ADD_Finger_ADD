#!/usr/bin/ python
# -*- coding:utf-8 -*-
"""
-------------------------------------------------
Author:       pugss
Datetime:     2024-12-10 12:47
ProjectName:  Finger.py
Blog:         https://www.testerwangxinsheng.top/
Email:        1270777250@qq.com
-------------------------------------------------
"""
import os
import concurrent.futures

import json
import sys
import requests
from urllib.parse import urlparse

requests.packages.urllib3.disable_warnings()
'''
-----ARL支持字段：-------
body = " "
title = ""
header = ""
icon_hash = ""
'''
if 1 < len(sys.argv) < 6:
    url = sys.argv[1]
    login_name = sys.argv[2]
    login_password = sys.argv[3]
    if len(sys.argv) >= 5:
        json_paths = sys.argv[4]
    else:
        json_paths = r"./json_path"
else:
    print('''
    usage:    python3 ARl-Finger-ADD.py https://192.168.1.1:5003/ admin password .
                                                        
                                                         by  wangxs
    ''')
    sys.exit(1)


def validate_url(url):
    """
    验证 URL 是否有效。

    参数:
    url (str): 要验证的 URL 字符串。

    返回:
    bool: 如果 URL 有效则返回 True，否则返回 False。
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_session(login_url, login_name, login_password):
    """
    获取登录令牌。

    参数:
    login_url (str): 登录 API 的 URL。
    login_name (str): 用户名。
    login_password (str): 密码。

    返回:
    requests.Session: 包含登录令牌的会话对象。

    异常:
    ValueError: 如果 URL 无效。
    requests.exceptions.RequestException: 如果请求失败。
    """
    if not validate_url(login_url):
        raise ValueError("Invalid login URL")

    str_data = {"username": login_name, "password": login_password}
    login_data = json.dumps(str_data)
    session = requests.Session()
    try:
        data = session.post(f"{login_url}api/user/login", headers={
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
            "Content-Type": "application/json; charset=UTF-8"}, data=login_data, verify=False)
        if "401" not in data.text:
            data.raise_for_status()
            token = data.json()['data']['token']
            session.headers.update({"Token": f"{token}"})
            return session
        else:
            print("账号或密码错误")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        sys.exit(1)


def run_thread(fingerprint_msg,session):
    body = "body=\"{}\""
    title = "title=\"{}\""
    hash = "icon_hash=\"{}\""

    finger_json = json.loads(json.dumps(fingerprint_msg))
    if finger_json['method'] == "keyword" and finger_json['location'] == "body":
        name = finger_json['cms']
        if len(finger_json['keyword']) > 0:
            for rule in finger_json['keyword']:
                rule = body.format(rule)
            else:
                rule = body.format(finger_json['keyword'][0])

    elif finger_json['method'] == "keyword" and finger_json['location'] == "title":
        name = finger_json['cms']

        if len(finger_json['keyword']) > 0:
            for rule in finger_json['keyword']:
                rule = title.format(rule)
            else:
                rule = title.format(finger_json['keyword'][0])
    else:
        name = finger_json['cms']
        if len(finger_json['keyword']) > 0:
            for rule in finger_json['keyword']:
                rule = hash.format(rule)
            else:
                rule = hash.format(finger_json['keyword'][0])

    url_add = f"{url}/api/fingerprint/"
    data = {"name": name, "human_rule": rule}
    try:
        response = session.post(url_add, json=data, verify=False)
        if response.status_code != 200 or response.json()['code'] not in [1609,1402,200]:
            print(f"{name} 添加失败 具体需要查看文件下详情 ，此时的错误为：{response.text}")
    except Exception as e:
        print(e)


def main(json_path, session):
    f = open(json_path, 'r', encoding="utf-8")
    content = f.read()
    load_dict = json.loads(content)
    data = load_dict['fingerprint']
    print(f"正在添加 {json_path}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(run_thread, data, [session] * len(data)))
    print(f"----------------{json_path} 所有指纹添加成功-------------------")

def get_json_name_from_path(file_path):
    '''获取指定文件夹下的 json 文件的路径'''
    return [os.path.join(file_path, file) for file in os.listdir(file_path) if file.endswith('.json')]


if __name__ == '__main__':
    try:
        json_lists = get_json_name_from_path(json_paths)
        session = get_session(url, login_name, login_password)
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
            list(executor.map(main, json_lists, [session] * len(json_lists)))
    except Exception as a:
        print(a)
