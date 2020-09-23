#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年08月27日 星期四 22时00分00秒
# Brief:
# Selenium爬取二手房信息
################################################################################
from selenium import webdriver
import json
import random
import re
import hashlib
from pymongo import MongoClient
from redis import StrictRedis
import logging
import time
import traceback
from multiprocessing.dummy import Pool as ThreadPool


DEFAULT_REDIS_URI = 'redis://localhost:6379/1'
DEFAULT_MONGO_URI = 'mongodb://myTestUser:abcd1234@localhost:27017/58info'
MONGO_COLL = 'ershoufang'

logger = logging.getLogger()
LOG_FILE = "58info.log"
logging.basicConfig(filename=LOG_FILE, format='%(filename)s :%(asctime)s : %(message)s', filemode='a')
logger.setLevel(logging.DEBUG)
redis = StrictRedis.from_url(DEFAULT_REDIS_URI)
mongo_client = MongoClient(DEFAULT_MONGO_URI)
mongo_db = mongo_client.get_default_database()
mongo_coll = mongo_db[MONGO_COLL]

driver = None


def get_proxy():
    '''从文件中读取高匿名代理，一定要检测为高匿名，否则58会获取用户真实IP地址'''
    with open('useful_proxy.list', 'r') as f:
        datas = f.readlines()
    proxy_list = [_.replace('\n', '') for _ in datas]
    return {'proxy': random.choice(proxy_list)}
    # return req.get("http://127.0.0.1:5030/get?check_out=100").json()


def get_driver():
    global driver
    if driver:
        return driver
    # PROXY = get_proxy().get('proxy')
    PROXY = 'socks5://127.0.0.1:1084'
    logger.info(f'proxy: {PROXY} .')
    USER_AGENT = 'user-agent="Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Mobile Safari/537.36"'
    options = webdriver.ChromeOptions()
    options.headless = True
    # options.headless = False
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument("--disable-infobars")
    options.add_argument('--proxy-server=%s' % PROXY)
    options.add_argument(USER_AGENT)

    driver = webdriver.Chrome(options=options)
    # 元素搜索超时时间
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(30)
    return driver


def get_city_json(file='city.list'):
    '''读取城市列表'''
    with open(file, 'r') as f:
        city_list = f.readlines()
    cityList_all = [_.replace('\n', '') for _ in city_list]
    city_info = {}
    for cityList in cityList_all:
        cityList = json.loads(cityList)
        for i in list(cityList):
            city_list = cityList[i]
            for j in list(city_list):
                idx = i + "-" + j
                city_info[idx] = city_list[j].split('|')[0]
    return city_info


def gen_city_list():
    '''生成redis访问城市列表'''
    city_list = get_city_json()   # 城市字典 {'黑龙江-哈尔滨': 'hrb' , ...}
    citys = []
    for i in list(city_list):
        print(i, city_list[i])
        val = {'name': i, 'value': city_list[i]}
        citys.append(val)
    return citys


def get_city_list(driver):
    '''
    获取城市列表信息及字母编号
    链接中需要用到字母编号，例如: 北京-bj ==> https://bj.58.com
    '''
    driver.get('https://www.58.com/changecity.html?fullpath=0')
    if '验证码' in driver.title:
        print('检测到需要验证码, 标题信息:' + driver.title)
        return False
    cityList, independentCityList = driver.execute_script('return cityList,independentCityList')
    cityList['直辖市'] = independentCityList
    # save_to_json
    with open('city.list', 'w') as f:
        f.write(json.dumps(cityList, ensure_ascii=False))
    return True


def get_city_ershoufang(driver, city):
    '''
    根据城市字母编号,二手房信息提取
    params:
        driver - webdriver句柄，控制浏览器
        city   - 城市字母编号，例如: bj
    '''
    url = f'https://m.58.com/{city}/ershoufang/0/'
    driver.get(url)
    if '验证码' in driver.title:
        print('检测到需要验证码, 标题信息:' + driver.title)
        return None
    return driver


def get_ershoufang_info(driver, name, city):
    '''
    解析页面中的二手房信息，单独提取出来的目的是方便页面访问异常(验证码、代理超时等)时问题处理。
    params : driver - webdriver驱动器句柄，用户解析页面内容
    '''
    xpath_item_info = './li[@class="list-item-info-addr"]/span[@class="list-item-info-addr-text"]'
    xpath_item_addr = './li[@class="list-item-info-subway"]/span'
    xpath_item_price = './li[@class="list-item-info-price"]/i'
    xpath_item_list = '//div[@class="list-container"]/ul/li[@post_type]'

    li_list = driver.find_elements_by_xpath(xpath_item_list)
    house_list = []
    for li in li_list:
        house_info = {}
        hurl = li.find_element_by_xpath('./a').get_attribute('href')
        url_id = re.sub(r'\?.+', '', hurl)
        hash_id = hashlib.md5(url_id.encode()).hexdigest()
        item = li.find_element_by_xpath('./a/ul[@class="list-item-info"]')
        item_info = item.find_element_by_xpath(xpath_item_info).text.strip().replace('㎡', '').split("|")
        item_addr = item.find_element_by_xpath(xpath_item_addr).text.strip()
        item_price = item.find_element_by_xpath(xpath_item_price).text.strip()

        house_info['type'] = item_info[0]
        house_info['area'] = float(item_info[1])
        house_info['community'] = item_info[2]
        house_info['total_price'] = float(item_price)
        house_info['price'] = (float(item_price)*10000)//float(item_info[1])
        house_info['address'] = item_addr
        house_info['url'] = url_id
        house_info['_id'] = hash_id
        house_info['city_code'] = city
        house_info['prov'] = name[0]
        house_info['city'] = name[1]
        # print(house_info)
        house_list.append(house_info)
    return house_list


def save_to_mongo(house_list):
    '''保存数据到mongodb， 使用redis集合作为url的(访问,信息)剔重'''
    count = 0
    total = 0
    doer = 0
    for hinfo in house_list:
        # 校验 URL是否访问过
        total += 1
        hash_id = hinfo['_id']
        url_id = hinfo['url']
        if redis.sismember('house_doer', hash_id):
            doer += 1
            logger.info("DOER: 重复访问的网址:{}, hash:{}, 忽略访问继续...".format(url_id, hash_id))
            continue
        redis.sadd('house_doer', hash_id)
        mongo_coll.insert_one(hinfo)
        count += 1
    # 显示入库结果
    logger.info(f'STAT_LOG: LOAD_SUCCESS ,总条数: {total} 条,入库总条数: {count} ,重单条数: {doer}')
    print(f'STAT_LOG: LOAD_SUCCESS ,总条数: {total} 条,入库总条数: {count} ,重单条数: {doer}')


def close(driver):
    if driver is not None:
        driver.close()


def process(city):
    '''处理所有的任务'''
    isLoop = False  # 是否循环下一页,默认关闭
    name = city['name']
    code = city['value']
    while True:
        try:
            driver = get_driver()
            get_city_ershoufang(driver, code)
            while True:
                house_list = get_ershoufang_info(driver, name.split('-'), code)
                save_to_mongo(house_list)
                next_page = None
                if isLoop is True:
                    xpath_nextpage = r'//nav[@class="page-nav"]/a[@tongji_tag="m_house_ersflist_nextpage"]'
                    next_page = driver.find_element_by_xpath(xpath_nextpage)

                if next_page:
                    logger.info("当前城市:" + name + " ,查找到下一页(sleep 10): [" + next_page.get_attribute('href') + " ]")
                    time.sleep(3)
                    next_page.click()
                else:
                    break
            break
        except Exception as e:
            traceback.print_exc()
            logger.error(f'当前城市: {name} 出现异常: 信息: ' + str(e))
        finally:
            if driver:
                driver.close()
        time.sleep(3)


print("init ok!")

driver = get_driver()

if __name__ == '__main__':
    pool = ThreadPool(5)
    try:
        get_city_list(driver)
        citys = gen_city_list()
        results = pool.map(process, citys)
    except Exception as e:
        print(e)
    pool.close()
    pool.join()
