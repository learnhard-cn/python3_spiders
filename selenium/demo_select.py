#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月18日 星期六 15时18分01秒
#########################################################################
from selenium import webdriver
from selenium.webdriver.support.select import Select
from time import sleep

driver = webdriver.Chrome()
driver.maximize_window()
driver.implicitly_wait(10)
driver.get('http://sc.chinaz.com/jiaobendemo.aspx?downloadid=5202032413289')
sleep(2)

frame = driver.find_element_by_id('iframe')
driver.switch_to.frame(frame)
sel = driver.find_element_by_id(r'form1')
Select(sel).select_by_value('guangdong')

sel = driver.find_element_by_id(r'form2')
Select(sel).select_by_value('shenzhen')

sel = driver.find_element_by_id(r'form3')
Select(sel).select_by_value('luohu')

#driver.switch_to.alert.accept()

# ……
sleep(10)
driver.quit()

