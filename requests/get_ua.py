#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月14日 星期二 22时26分33秒
# Brief: 获取User-Agent列表
#########################################################################

import requests as req
from lxml import etree
import re

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
}
def main():
    browser_list = ["Chrome", "Firefox", "Edge", "ChromePlus", "Opera",]
    for browser in browser_list:
        url='http://useragentstring.com/pages/useragentstring.php?name=' + browser
        resp = req.get(url, headers = headers)
        doc = etree.HTML(resp.text)
        ua_list = doc.xpath('//ul/li/a/text()')
        uas = '\n'.join(ua_list)
        uas = uas.replace(' Mozilla','\nMozilla')
        print(uas)

if __name__ == '__main__':
    main()
