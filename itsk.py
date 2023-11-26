# !/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : wjf0214
# @Time : 2023/11/25 23:23
# -------------------------------
# cron "30 8 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('IT天空网站签到')

"""
IT天空网站签到
export itskCookie = 'access_itsk=Bearer***',多账号使用换行或&
cookie取网站首页cookie
"""

import requests
import os
import sys
import time
import random
import string
import hashlib
import msg as notify

from urllib.parse import unquote

ck_list = []

sign_url = "https://api.itsk.com/webapi/sign"
headers = {
    'Accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://www.itsk.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'Sec-Ch-Ua-Mobile': "?0",
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Origin': 'https://www.itsk.com'
}


# 签到
def sign_in(cookie):
    try:
        access_itsk = get_cookie_value(cookie, 'access_itsk')
        headers = get_header(access_itsk)

        # {"code":200,"message":"签到成功","data":{"total":1,"credit":"活跃","message":null,"month_days":2,"days":697,"status":0}}
        response = requests.get(sign_url, headers=headers).json()

        if response.get('code') == 200:
            if response.get('data').get('status') == 0:
                msg = f"{response.get('message')} --- 恭喜获得 {response.get('data').get('total')} {response.get('data').get('credit')} , 本月签到共 {response.get('data').get('month_days')} 天，总共签到 {response.get('data').get('days')} 天"
            else:
                msg = f"{response.get('message')} --- 累计获得 {response.get('data').get('total')} {response.get('data').get('credit')} , 本月签到共 {response.get('data').get('month_days')} 天，总共签到 {response.get('data').get('days')} 天"
            notify.info_message(msg)
        else:
            notify.error_message(f"签到失败！--- {response.get('message')}")
    except Exception as err:
        notify.error_message(f"Unexpected {err=}, {type(err)=}")


# 获取环境变量
def get_env():
    global ck_list
    env_str = os.getenv("itskCookie")
    if env_str:
        ck_list += env_str.replace("&", "\n").split("\n")


# 随机字符串
def nonce(t=32):
    e = string.ascii_letters + string.digits
    r = ''.join(random.choice(e) for _ in range(t))
    return r


# sha1加密
def sha1(t, e):
    n = e[:4]
    r = e[-4:]
    return hashlib.sha1(f"{n}{t}{r}{e}".encode('utf-8')).hexdigest()


# 获取请求头
def get_header(access_itsk):
    global headers
    timestamp = int(time.time())
    nonceStr = nonce()
    encrypt = sha1(timestamp, nonceStr)
    header = {
        "Authorization": access_itsk,
        "X-Request-timestamp": str(timestamp),
        "X-Request-signature": encrypt,
        "X-Request-nonce": nonceStr
    }
    return {**header, **headers}


# 获取cookie
def get_cookie_value(cookie, key):
    cookie = unquote(cookie)
    cookie_parts = cookie.split(";")
    for part in cookie_parts:
        if key in part:
            return part.split("=")[1]
    return None


def main():
    get_env()

    if not ck_list:
        notify.error_message('没有获取到cookie。')
        return

    notify.info_message(f'获取到{len(ck_list)}个账号！')

    for index, ck in enumerate(ck_list):
        notify.info_message(f'*****第{index + 1}个账号*****')
        # 签到
        sign_in(ck)


if __name__ == '__main__':
    notify.init()
    main()
    notify.send_notify("IT天空 每日签到")
