#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月18日 星期六 20时04分41秒
#########################################################################
import time
import requests as req
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType


PROXY = req.get('http://localhost:5030/get').json()['proxy']

print(PROXY)

proxy = Proxy()
proxy.http_proxy = PROXY
proxy.ssl_proxy = PROXY

capabilities = webdriver.DesiredCapabilities.FIREFOX
proxy.add_to_capabilities(capabilities)

with webdriver.Firefox(desired_capabilities=capabilities) as driver:
   driver.get("https://httpbin.org/ip")
   print(driver.title)
   time.sleep(5)
