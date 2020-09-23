#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月14日 星期二 22时26分33秒
#########################################################################

import requests as req
import html

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
}
# 获取贴吧信息：
#   排名序号|标题|摘要|热度|链接图片
def tieba_hot():
    url='https://jump.bdimg.com/hottopic/browse/topicList'
    # JSON数据接口
    resp = req.get(url, headers = headers)
    data = resp.json()
    topic_list = data['data']['bang_topic']['topic_list']
    for topic in topic_list:
        topic_url = html.unescape(topic['topic_url'])
        #print('{} |{}|{}\n{}'.format(topic['idx_num'],topic['topic_name'],topic['topic_desc'],topic_url))
        print('{} |{}|{}\n'.format(topic['idx_num'],topic['topic_name'],topic_url))

if __name__ == '__main__':
    tieba_hot()
