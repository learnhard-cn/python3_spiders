#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月14日 星期二 22时26分33秒
#########################################################################

import requests as req
from lxml import etree
import urllib.parse as parse
import html

headers = {
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25',
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,zh-TW;q=0.5",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1"
}

## //*[@id="root"]/div/main/div/div[2]/div[1]
# 获取知乎热搜
def zhihu_topsearch():
    url='https://www.zhihu.com/topsearch'
    # JSON数据接口
    resp = req.get(url, headers = headers)
    doc = etree.HTML(resp.text)
    topic_list = doc.xpath('//div[@class="TopSearchMain-list"]/div')
    print(len(topic_list))
    for topic in topic_list:
        title = topic.xpath('div/div[@class="TopSearchMain-title"]/text()')[0]
        sub_title = topic.xpath('div/div[@class="TopSearchMain-subTitle"]/text()')[0]
        print(f'[{title} ]  [{sub_title}]\n---------------------')

if __name__ == '__main__':
    zhihu_topsearch()
