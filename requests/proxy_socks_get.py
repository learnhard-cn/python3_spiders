#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月13日 星期一 16时08分15秒
#########################################################################
import requests as req

proxies = {
        'http'  : 'socks5://127.0.0.1:1080',
        'https' : 'socks5://127.0.0.1:1080'
}

print(f'代理地址：{proxies}')

resp = req.get('https://httpbin.org/ip', proxies = proxies)
print(resp.text)

url = 'https://www.google.com'
resp = req.get(url, proxies = proxies)
print(f'返回状态码:{resp.status_code}')
