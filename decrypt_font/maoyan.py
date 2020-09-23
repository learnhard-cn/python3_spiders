#!/usr/bin/env python3
# -*-coding:utf8-*-
import logging
import traceback
import requests
from requests.adapters import HTTPAdapter
import json
import random
import pymysql
import sys
import datetime
import time
from lxml import etree
import argparse
from dp_font import GlypFont
import re


parser = argparse.ArgumentParser('猫眼网信息爬虫')
parser.add_argument('-p', '--page', default=1, type=int, help='设置搜索页数,默认1页')
parser.add_argument('-t', '--thread', default=1, type=int, help='设置并发线程数,默认1页')
parser.add_argument('-o', '--output', default='out.json', help='输出到文件名')

parse_result = parser.parse_args()
pn = parse_result.page
output_file = parse_result.output

# 板块ID,

LOG_FORMAT = "%(asctime)s - %(filename)s - %(funcName)s - %(lineno)s - %(levelname)s - %(message)s"
logging.basicConfig(filename=f'log.maoyan.log', level=logging.INFO, filemode='a', format=LOG_FORMAT)


def get_proxy():
    '''
    获取代理池IP
    '''
    proxy_pool = "http://127.0.0.1:5030/get?check_count=500&type=http&resp_seconds=5"
    resp_proxy = requests.get(proxy_pool)
    prinfo = resp_proxy.json()
    proxy_uri = prinfo['proxy']
    proxy_type = prinfo['type'].lower()
    # 如果为空默认为http协议代理
    proxy_type = proxy_type if proxy_type != "" and proxy_type is not None else "http"
    proxies = {
        'http': proxy_type + '://' + proxy_uri,
        'https': proxy_type + '://' + proxy_uri
    }
    return proxies


def write_to_json(file, data_list):
    '''
    从Json数据文件中读取数据
    '''
    with open(file, 'w') as js_file:
        for row in data_list:
            js_file.write(json.dumps(row, ensure_ascii=False) + '\n')


class Maoyan():
    '''
    爬取猫眼电影榜单信息
    '''
    xpath_dd = r'//dl[@class="board-wrapper"]/dd'
    xpath_title = r'./div/div/div[@class="movie-item-info"]/p[@class="name"]/a/text()'
    xpath_star = r'./div/div/div[@class="movie-item-info"]/p[@class="star"]/text()'
    xpath_releasetime = r'./div/div/div[@class="movie-item-info"]/p[@class="releasetime"]/text()'
    xpath_realtime = r'./div/div/div[@class="movie-item-number boxoffice"]/p[@class="realtime"]'
    xpath_total = r'./div/div/div[@class="movie-item-number boxoffice"]/p[@class="total-boxoffice"]'
    xpath_img_url = r'./a/img["board-img"]/@data-src'
    xpath_score = r'./div/div/div[@class="movie-item-number score-num"]/p[@class="score"]'
    xpath_want_month = r'./div/div/div[@class="movie-item-number wish"]/p[@class="month-wish"]'
    xpath_want_total = r'./div/div/div[@class="movie-item-number wish"]/p[@class="total-wish"]'
    urls = {
        # collection_name : [ url, page, page_type[money,score,wish], useFont]
        'board_cn': ['https://maoyan.com/board/1', 1, 'm', True],  # 国内票房榜
        'board_us': ['https://maoyan.com/board/2', 1, 'm', True],  # 北美票房榜
        'board_top': ['https://maoyan.com/board/4', 10, 's', False],  # Top100
        'board_want': ['https://maoyan.com/board/6', 5, 'w', True],  # 最受期待榜
        'board_talk': ['https://maoyan.com/board/7', 1, 's', False]  # 热映口碑榜
    }

    def __init__(self, headers=None, proxies=None, retries=3, timeout=10):
        '''
        创建Session信息
        '''
        self.my_font = GlypFont('maoyan')
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.host = 'https://maoyan.com/'
        self.timeout = timeout
        self.headers = headers
        if self.headers is None:
            self.headers = self.get_headers()

        self.proxies = proxies
        if self.proxies is None:
            self.proxies = None
            # self.proxies = get_proxy()

        try:
            resp = self.session.get(self.host, headers=self.headers, proxies=self.proxies, timeout=self.timeout)
            print(resp.url, self.host)
            if resp.url != self.host:
                raise Exception("可能出现验证码问题!请重新尝试!")
        except Exception as e:
            print(e)

    def get_headers(self):
        '''
        返回默认Header
        '''
        return {
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
            'Referer': 'https://maoyan.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,zh-TW;q=0.5'
        }

    def get_board_top(self, url, page, p_type, useFont):
        '''
        爬取 评价榜(口碑,期待,TOP100)信息
        params:
            url: 页面URL地址
            page: 页数
            p_type: m -(money)票房,s -(score)评分
        '''
        result = []
        n_url = url
        try:
            for idx in range(0, page):
                if idx > 0:
                    n_url = url + '?offset=' + str(idx*10)
                resp = self.session.get(n_url, proxies=self.proxies, timeout=self.timeout, headers=self.headers)
                resp_data = resp.text
                print(n_url, resp.url)
                logging.info(f'n_url:{n_url}, cur_url:{resp.url}')
                if n_url != resp.url:
                    # 可能出现验证码，退出 #
                    logging.info(f"{n_url} : 可能出现验证码情况，请重新尝试!")
                    break
                if useFont:
                    # 需要字体处理: 获取编码字典，并替换页面中的编码
                    font_url = 'http:' + re.search(r"url\('(.+\.woff)?'\)", resp_data).group(1)
                    font_dict = self.my_font.getFont(font_url)
                    for key in font_dict.keys():
                        resp_data = resp_data.replace(key, font_dict[key])

                doc = etree.HTML(resp_data)
                dd_list = doc.xpath(self.xpath_dd)
                if dd_list is None or len(dd_list) < 1:
                    # 页面解析错误,跳过当前页
                    continue
                for dd in dd_list:
                    data = {}
                    data['_id'] = int(dd.xpath(r'./i/text()')[0])
                    data['title'] = dd.xpath(self.xpath_title)[0].strip()
                    try:
                        data['star'] = dd.xpath(self.xpath_star)[0].strip()
                    except:
                        data['star'] = ""
                    str_time = dd.xpath(self.xpath_releasetime)[0].split("：")[1]
                    data['releasetime'] = str_time
                    data['year'] = int(str_time[0:4])
                    if p_type == 'm':  # 票房榜
                        tmp_data = dd.xpath(self.xpath_realtime)[0].xpath(r'string(.)').strip('实时票房：: \t\n')
                        tmp_idx = tmp_data.find('亿')
                        if tmp_idx != -1:
                            tmp_value = float(tmp_data[0:tmp_idx]) * 10000
                            data['realtime'] = str(tmp_value) + '万'
                        else:
                            data['realtime'] = tmp_data
                        tmp_data = dd.xpath(self.xpath_total)[0].xpath(r'string(.)').strip('总票房：: \t\n')
                        tmp_idx = tmp_data.find('亿')
                        if tmp_idx != -1:
                            tmp_value = float(tmp_data[0:tmp_idx]) * 10000
                            data['total_box'] = str(tmp_value) + '万'
                        else:
                            data['total_box'] = tmp_data
                    elif p_type == 's':  # 评分榜
                        data['score'] = float(dd.xpath(self.xpath_score)[0].xpath(r'string(.)').strip())
                    elif p_type == 'w':  # 心愿榜
                        data['wish_month'] = int(dd.xpath(self.xpath_want_month)[0].xpath(r'string(.)').strip('本月新增想看： 人\t\n'))
                        data['wish_total'] = int(dd.xpath(self.xpath_want_total)[0].xpath(r'string(.)').strip('总想看：  人\t\n'))
                    data['img_url'] = dd.xpath(self.xpath_img_url)[0].split("@", maxsplit=1)[0]  # 去掉缩略图信息
                    result.append(data)
                time.sleep(3)
        except requests.exceptions.ProxyError as e:
            logging.error('proxy_error ' + str(e))
        except Exception as e:
            logging.exception('proxy: ' + str(e))
        return result

    def fetch_all(self):
        '''
        爬取所有页面数据,并且输出到JSON文件中
        '''
        try:
            # import db_mongo as db
            # mongo = db.MongoDb(**db.default_config)
            for key in list(self.urls):
                url, page, p_type, useFont = self.urls[key]
                result = self.get_board_top(url, page, p_type, useFont)
                file_name = "maoyan_" + key + ".json"
                write_to_json(file_name, result)
                # mongo.change_collection('maoyan_' + key)
                # if result is not None and len(result) > 1:
                #     mongo.upsert(result)
                # else:
                #     print("no result to write!")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    try:
        maoyan = Maoyan()
        maoyan.fetch_all()
    except Exception as e:
        print(e)
