#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月13日 星期一 14时39分52秒
#########################################################################

import requests

url = 'https://www.baidu.com'
try:
    resp = requests.get(url, timeout = (0.01,3))
    print(resp.status_code)
    if resp.status_code == 200:
        print(resp.text[:50])
except requests.exceptions.ConnectTimeout as e:
    print('连接超时: ' + str(e))
