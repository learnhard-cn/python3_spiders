#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月13日 星期一 16时00分39秒
#########################################################################
import requests as req

proxies = { 
    'http'  : '114.239.88.195:4216',
    'https' : '114.239.88.195:4216'
}

print(f'代理地址：{proxies}')

resp = req.get('https://httpbin.org/ip', proxies = proxies)
print(resp.text)

