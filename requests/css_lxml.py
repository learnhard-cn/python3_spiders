#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月14日 星期二 19时30分27秒
#########################################################################

import requests as req
from lxml import etree

url='https://www.learnhard.cn'

resp = req.get(url)
doc = etree.HTML(resp.content)
title_list = doc.cssselect('article > header > h2 > a')
for item in title_list:
    title = item.text
    url = item.attrib['href']
    print(url, title)
