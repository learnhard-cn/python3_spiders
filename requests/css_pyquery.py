#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月14日 星期二 19时30分27秒
#########################################################################

import requests as req
from pyquery import PyQuery as pq

url='https://www.learnhard.cn'

resp = req.get(url)
query = pq(resp.content)

item_list = query('article > header > h2 > a')
print(item_list)
for item in item_list:
    title = item.text
    url = item.attrib['href']
    print(url, title)
