#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年08月05日 星期三 20时24分54秒
# Brief:
################################################################################

import sys

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import requests
from io import BytesIO


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
}

my_threshold = 100
if len(sys.argv) > 2:
    my_threshold = int(sys.argv[2])
def get_bin_table(threshold=my_threshold):
    """
    图片二值化处理
    """
    def bin_num(n):
        return 0 if n < threshold else 1
    return [bin_num(i) for i in range(256)]

def sum_9_region_new(img, x, y):
    '''确定噪点 '''
    cur_pixel = img.getpixel((x, y)) # 当前像素点的值
    width = img.width
    height = img.height

    if cur_pixel == 1:  # 当前点为白色点,不统计
        return 0

    # 当前点为黑点, 判断周围相邻点
    if y < 3: # 边界点直接去除,
        return 1
    elif y > height - 3: # 最下面两行
        return 1
    else: # y不在边界
        if x < 3: # 前两列
            return 1
        elif x == width - 1: # 右边非顶点
            return 1
        else: # 计算相邻点黑色块数量
            sum = img.getpixel((x - 1, y - 1)) \
                 + img.getpixel((x - 1, y)) \
                 + img.getpixel((x - 1, y + 1)) \
                 + img.getpixel((x, y - 1)) \
                 + cur_pixel \
                 + img.getpixel((x, y + 1)) \
                 + img.getpixel((x + 1, y - 1)) \
                 + img.getpixel((x + 1, y)) \
                 + img.getpixel((x + 1, y + 1))
            return 9 - sum

def collect_noise_point(img):
    '''收集所有的噪点'''
    noise_point_list = []
    for x in range(img.width):
        for y in range(img.height):
            res_9 = sum_9_region_new(img, x, y)
            if (0 < res_9 < 4) and img.getpixel((x, y)) == 0: # 找到孤立点
                pos = (x, y)
                noise_point_list.append(pos)
    return noise_point_list

def remove_noise_pixel(img, noise_point_list):
    '''根据噪点的位置信息，消除二值图片的黑点噪声'''
    for item in noise_point_list:
        img.putpixel((item[0], item[1]), 1)


# 核心处理逻辑
def ocr_core(filename):
    """
    This function will handle the core OCR processing of images.
    """
    img = None
    if filename.startswith('http'):
        # 从URL中获取图片
        resp = requests.get(filename, headers=headers)
        img = Image.open(BytesIO(resp.content))
    else:
        img = Image.open(filename)
    # 灰度处理
    imgry = img.convert("L")
    imgry.save('img_gray.png')

    # 二值化处理
    table = get_bin_table()
    imgbin = imgry.point(table, "1")
    imgbin.save('img_bin.png')

    # 降噪处理(边缘连接判断)
    noise_point_list = collect_noise_point(imgbin)
    remove_noise_pixel(imgbin, noise_point_list)
    imgbin.save('img_out.png')


    custom_oem_psm_config = r'--tessdata-dir /apps/share/tessdata/best --oem 3 --psm 6 -l chi_sim+eng'
    text = pytesseract.image_to_string(imgbin, config=custom_oem_psm_config)
    return text
    # return text.replace(' ', '').strip()

print(ocr_core(sys.argv[1]))
