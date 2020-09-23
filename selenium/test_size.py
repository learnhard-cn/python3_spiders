#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月18日 星期六 14时53分49秒
#########################################################################

from selenium import webdriver
import time

driver = webdriver.Chrome()
driver.get("http://www.baidu.com")

driver.maximize_window()
size = driver.get_window_size()
print(size.get('width'),size.get('height'))
time.sleep(1)
driver.fullscreen_window()

time.sleep(3)
# 获得输入框的尺寸
size = driver.find_element_by_id('kw').size
print(size)

time.sleep(3)
# 返回百度页面底部备案信息
text = driver.find_element_by_id("s-bottom-layer-right").text
print(text)

time.sleep(3)
# 返回元素的属性值， 可以是 id、 name、 type 或其他任意属性
attribute = driver.find_element_by_id("kw").get_attribute('type')
print(attribute)

time.sleep(3)
# 返回元素的结果是否可见， 返回结果为 True 或 False
result = driver.find_element_by_id("kw").is_displayed()
print(result)

driver.quit()

