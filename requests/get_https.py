#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月13日 星期一 15时04分57秒
#########################################################################
import requests as req

url = 'https://httpbin.org/anything'
resp = req.get(url, verify = False)
print(resp.status_code)
