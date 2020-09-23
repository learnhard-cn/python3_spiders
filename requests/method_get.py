#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月13日 星期一 15时30分45秒
#########################################################################
import requests as req

payload1 = {
        'name': 'Peter',
        'age': 23
}
payload2 = {
        'name': 'Peter',
        'seen_list': [1,2,3,4,5,6]
}
url = 'https://httpbin.org/get'

resp = req.get(url, params=payload1)
print(resp.url)

resp = req.get(url, params=payload2)
print(resp.url)

