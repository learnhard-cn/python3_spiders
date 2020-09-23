#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月14日 星期二 19时30分27秒
#########################################################################

import requests as req
from bs4 import BeautifulSoup  as bs

url='https://www.learnhard.cn'

resp = req.get(url)
soup = bs(resp.content, 'lxml')
item_list = soup.select('article > header > h2 > a')
for item in item_list:
    title = item.get_text().strip()
    url = item.attrs['href']
    print(url, title)
