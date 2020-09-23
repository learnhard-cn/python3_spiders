#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月14日 星期二 22时26分33秒
#########################################################################

import requests as req
from lxml import etree
import re

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'authority': 'weibo.com',
    'cookie': 'UM_distinctid=171437c9856a47-0cd9abe048ffaf-1528110c-1fa400-171437c9857ac3; CNZZDATA1272960323=1824617560-1569466214-%7C1595951362; SCF=AhjAkJNek3wkLok6WSbiibV1WsGffKPYsDlTZtFqiUH_YWL81nk-0xKkiukxpRoDMoIoV0IClwWecgXLLPiBZrw.; SUHB=0gHTlGutSIGq9P; ALF=1628229198; SUB=_2AkMoasG0f8NxqwJRmfoUxG7ibIl_ww7EieKeNjBvJRMxHRl-yT9jqlYktRB6A-rvW2hROYk5DlHgX7r_dk67bcEdfhBN; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WWh..ORuiFeK.mEWDWeecX1; SINAGLOBAL=1133654064055.2583.1597394566906; UOR=,,www.comicyu.com; login_sid_t=f855cdd8714fdb25dee824ce5ff8d792; cross_origin_proto=SSL; Ugrow-G0=6fd5dedc9d0f894fec342d051b79679e; TC-V5-G0=4de7df00d4dc12eb0897c97413797808; wb_view_log=1914*10771.0026346445083618; _s_tentry=weibo.com; Apache=4531467438705.743.1597800659782; ULV=1597800659793:3:2:1:4531467438705.743.1597800659782:1597394566920; TC-Page-G0=d6c372d8b8b800aa7fd9c9d95a471b97|1597800912|1597800912; WBStorage=42212210b087ca50|undefined'
}
def main():
    url='https://weibo.com/a/hot/realtime'
    resp = req.get(url, headers = headers)
    # print(resp.text)
    doc = etree.HTML(resp.text)
    topic_list = doc.xpath('//div[@class="UG_content_row"]')
    for topic in topic_list:
        desc = topic.xpath('.//div[@class="list_des"]')[0]
        topic_title = desc.xpath('h3[@class="list_title_b"]/a/text()')[0].strip()
        subinfo = desc.xpath('./div')[0].xpath('string(.)').strip().replace(' ','')
        subinfo = re.sub('\s+',',', subinfo)
        subinfo = re.findall(r'(.*?),(.*?),.*?([0-9]*?),.*?([0-9]*?),.*?([0-9]+)', subinfo)[0]
        print(topic_title + ',' + ','.join(subinfo))

if __name__ == '__main__':
    main()
