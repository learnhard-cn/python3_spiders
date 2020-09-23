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

PROXY = req.get('http://localhost:5030/get/?check_count=100&resp_seconds=10&type=http').json()['proxy']
print(PROXY)
webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
    "httpProxy": PROXY,
    "ftpProxy": PROXY,
    "sslProxy": PROXY,
    "proxyType": "MANUAL",
}

print("firefox")
driver = webdriver.Firefox() 

driver.get("https://www.bilibili.com/video/BV194411g7EH")
print(driver.title)
time.sleep(5)
