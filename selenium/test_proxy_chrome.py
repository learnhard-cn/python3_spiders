#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月18日 星期六 19时23分18秒
#########################################################################
from selenium import webdriver
import time
import requests as req

PROXY = req.get('http://localhost:5030/get').json()['proxy']

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--proxy-server=%s' % PROXY)
with webdriver.Chrome(options=chrome_options) as driver:
        driver.get("https://httpbin.org/ip")
        print(driver.title)
        time.sleep(5)

