#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月13日 星期一 15时30分45秒
#########################################################################
import requests as req

payload = {
        'name': 'Peter',
        'age': 23
}
url = 'https://httpbin.org/post'

resp = req.post(url, data=payload)
print(resp.text)

