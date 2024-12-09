#!/usr/bin/ python
# -*- coding:utf-8 -*-
"""
-------------------------------------------------
Author:       loecho
Datetime:     2021-07-23 12:47
ProjectName:  getFinger.py
Blog:         https://loecho.me
Email:        loecho@foxmail.com
-------------------------------------------------
"""
import os
import sys
import json
import requests
import concurrent.futures

requests.packages.urllib3.disable_warnings()

'''
-----ARL支持字段：-------
body = " "
title = ""
header = ""
icon_hash = ""
'''


def run_thread(url, token, fingerprint_msg):
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
            add_Finger(name, rule, url, token)

    elif finger_json['method'] == "keyword" and finger_json['location'] == "title":
        name = finger_json['cms']

        if len(finger_json['keyword']) > 0:
            for rule in finger_json['keyword']:
                rule = title.format(rule)
            else:
                rule = title.format(finger_json['keyword'][0])
            add_Finger(name, rule, url, token)
    else:
        name = finger_json['cms']
        if len(finger_json['keyword']) > 0:
            for rule in finger_json['keyword']:
                rule = hash.format(rule)
            else:
                rule = hash.format(finger_json['keyword'][0])
            add_Finger(name, rule, url, token)


def main(url, token, json_path):
    f = open(json_path, 'r', encoding="utf-8")
    content = f.read()
    load_dict = json.loads(content)

    data = load_dict['fingerprint']

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        list(executor.map(run_thread, [url] * len(data), [token] * len(data),
                          data))


def add_Finger(name, rule, url, token):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
        "Connection": "close",
        "Token": "{}".format(token),
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Content-Type": "application/json; charset=UTF-8"
    }
    url = "{}/api/fingerprint/".format(url)
    data = {"name": name, "human_rule": rule}
    data_json = json.dumps(data)

    try:
        response = requests.post(url, data=data_json, headers=headers, verify=False)
        if response.status_code == 200:
            print(''' Add: [\033[32;1m+\033[0m]  {}\n Rsp: [\033[32;1m+\033[0m] {}'''.format(data_json, response.text))
    except Exception as e:
        print(e)


def test(name, rule):
    return print("name: {}, rule: {}".format(name, rule))


def get_json_name_from_path(file_path):
    '''获取指定文件夹下的 json 文件的路径'''
    return [os.path.join(file_path, file) for file in os.listdir(file_path) if file.endswith('.json')]


if __name__ == '__main__':
    try:
        if 1 < len(sys.argv) < 6:

            login_url = sys.argv[1]
            login_name = sys.argv[2]
            login_password = sys.argv[3]
            if len(sys.argv) >= 5:
                json_paths = sys.argv[4]
            else:
                json_paths = "."

            # login
            str_data = {"username": login_name, "password": login_password}
            login_data = json.dumps(str_data)
            login_res = requests.post(url="{}api/user/login".format(login_url), headers={
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
                "Content-Type": "application/json; charset=UTF-8"}, data=login_data, verify=False)

            # 判断是否登陆成功：
            if "401" not in login_res.text:

                # print(type(login_res.text))
                token = json.loads(login_res.text)['data']['token']
                print("[+] Login Success!!")
                json_lists = get_json_name_from_path(json_paths)

                with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
                    list(executor.map(main, [login_url] * len(json_lists), [token] * len(json_lists),
                                      json_lists))
                    executor.shutdown(wait=True)

            else:
                print("[-] login Failure! ")
        else:
            print('''
    usage:
        
        python3 ARl-Finger-ADD.py https://192.168.1.1:5003/ admin password .
                                                        
                                                         by  loecho
            ''')
    except Exception as a:
        print(a)
