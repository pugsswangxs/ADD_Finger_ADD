#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import sys
import requests
from urllib.parse import urlparse

requests.packages.urllib3.disable_warnings()


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


def get_token(login_url, login_name, login_password):
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


def delete_finger(session, login_url):
    """
    删除所有指纹。

    参数:
    session (requests.Session): 包含登录令牌的会话对象。
    login_url (str): 登录 API 的 URL。

    异常:
    ValueError: 如果 URL 无效。
    requests.exceptions.RequestException: 如果请求失败。
    """
    if not validate_url(login_url):
        raise ValueError("Invalid login URL")

    while True:
        try:
            url = f"{login_url}/api/fingerprint/?page=1&size=500"
            data = session.get(url=url, verify=True).json()
            if data['total'] == 0 or len(data['items']) < 1:
                break
            else:
                id_list = [i['_id'] for i in data['items']]
                if id_list:
                    delete_url = f"{login_url}/api/fingerprint/delete/"
                    data = {'_id': id_list}
                    session.post(url=delete_url, json=data, verify=True)
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            break
    print("----------------所有指纹删除成功-------------------")


if __name__ == '__main__':
    try:
        if 1 < len(sys.argv) < 5:
            login_name = sys.argv[1]
            login_password = sys.argv[2]
            login_url = sys.argv[3]
            session = get_token(login_url, login_name, login_password)
            delete_finger(session, login_url)
        else:
            print("Usage:python3 ARL-Finger-DELETE.py <login_name> <login_password> <login_url>")
    except Exception as e:
        print(f"Error: {e}")
