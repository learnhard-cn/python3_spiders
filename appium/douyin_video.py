#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年08月07日 星期五 21时10分21秒
# Brief:
################################################################################
# Android environment
import unittest
from appium import webdriver
from time import sleep


class DouYin(object):

    def __init__(self):
        self.desired_caps = {
            'platformName': 'Android',
            'automationName': 'UiAutomator2',
            'platformVersion': '5.1.1',
            'deviceName': '192.168.50.97:5555',
            'appPackage': 'com.ss.android.ugc.aweme',
            'appActivity': '.main.MainActivity'
        }
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', self.desired_caps)
        # 当资源未加载出时,最大等待时间3S
        self.driver.implicitly_wait(3)

    def unlock_windows(self):
        # 得到设备屏幕分辨率宽高
        win_size = self.driver.get_window_size()
        width = win_size['width']
        height = win_size['height']
        start_y = height//2
        end_y = 0
        start_x = width//2
        key = "learnhard.cn"
        # 上滑动 显示密码界面
        self.driver.swipe(start_x, start_y, start_x, end_y)
        elem = self.driver.find_element_by_id('com.smartisanos.keyguard:id/passwordEntry_comp')  # 输入密码框
        if elem is not None:
            elem.send_keys(key)
            self.driver.find_element_by_id('com.smartisanos.keyguard:id/passwordConfirmButton').click()  # 确认登录
        else:
            print("没找到复杂密码模式文本框元素")
            for i in key:
                self.driver.find_element_by_accessibility_id(i).click()

    def wait_for_alert(self, id, comment, count=3, per_sec=1):
        '''
        处理提示框，并关闭它
        '''
        for _ in range(count):
            try:
                elem = self.driver.find_element_by_id(id)
                elem.click()
                break
            except:
                pass
            sleep(per_sec)

    def swipe_video(self, count=30, per_sec=3):
        '''
        滑动douYin视频
        '''
        self.wait_for_alert('com.ss.android.ugc.aweme:id/ahw', '同意协议对话框', count=2)
        self.wait_for_alert('com.ss.android.ugc.aweme:id/dxm', '青少年模式对话框', count=0)
        self.wait_for_alert('com.ss.android.ugc.aweme:id/bbn', '升级提醒对话框', count=0)

        try:
            win_size = self.driver.get_window_size()
            width = win_size['width']
            height = win_size['height']
            start_y = height//2
            end_y = 0
            start_x = width//2
            self.driver.swipe(start_x, start_y, start_x, end_y)  # 第一次提示滑动
            for i in range(count):  # 循环滑动次数
                self.driver.swipe(start_x, start_y, start_x, end_y)  # 循环 从上向下滑动 产生请求视频链接接口调用(当然也可以反向滑动)
                sleep(per_sec)
        except:
            pass

    def pass_windows(self):
        # 得到设备屏幕分辨率宽高
        win_size = self.driver.get_window_size()
        print(win_size['width'], win_size['height'])
        # 检测锁屏状态
        elem_time = None
        try:
            elem_time = self.driver.find_element_by_id("com.smartisanos.keyguard:id/tv_time")
        except:
            pass
        if elem_time:
            self.unlock_windows()
        else:
            print("屏幕没有锁屏")

        # 刷动短视频
        self.swipe_video(10)

    # 关闭App
    def close_app(self):
        self.driver.close_app()

    def run(self):
        self.pass_windows()
        self.close_app()

if __name__ == '__main__':

    while True:
        try:
            douyin = DouYin()
            douyin.run()
        except Exception as e:
            print(e)
            break
#
