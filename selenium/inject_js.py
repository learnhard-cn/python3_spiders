#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年08月23日 星期日 16时00分01秒
# Brief: 
################################################################################


t0 = r'Object.defineProperties(navigator,{webdriver:{get:() => "undefined"}});'

def response(flow):
	if '.js' in flow.request.url:
		flow.response.text = t0 + flow.response.text
		print('注入成功')

