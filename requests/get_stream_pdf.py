#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月13日 星期一 19时44分15秒
#########################################################################

import requests as req

url = 'https://docs.oracle.com/javase/specs/jls/se14/jls14.pdf'

filename = url.split('/')[-1]

# 当在请求中将stream设为True后，`Requests`无法将连接自动释放回连接池，需要读取完所有数据或者手动调用`Requests.close`。
with req.get(url,stream=True) as r:
    with open(filename,'wb') as f:
        f.write(r.content)
