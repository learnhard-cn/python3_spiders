#!/usr/bin/env python3
# -*-coding:utf8-*-
from threading import Thread
import logging
import traceback
import requests
from requests.adapters import HTTPAdapter
import json
import re
import time
from lxml import etree
import argparse
from dp_font import GlypFont


parser = argparse.ArgumentParser('点评网信息爬虫')
parser.add_argument('-p', '--page', default=1, type=int, help='设置搜索页数,默认1页')
parser.add_argument('-o', '--output', default='out.json', help='输出到文件名')

parse_result = parser.parse_args()
pn = parse_result.page
output_file = parse_result.output

LOG_FORMAT = "%(asctime)s - %(filename)s - %(funcName)s - %(lineno)s - %(levelname)s - %(message)s"
logging.basicConfig(filename=f'log.dianping.log', level=logging.INFO, filemode='a', format=LOG_FORMAT)


def get_proxy():
    socks = 'socks5://127.0.0.1:1084'
    proxies = {
        'http': socks,
        'https': socks,
    }
    return proxies


class Dianping():
    '''
    爬取点评网美食店铺信息
    '''
    xpath_nav = r'//div[@class="nav-category J_filter_channel"]//div[@class="nc-items"]/a'
    xpath_page_num = r'//div[@class="page"]/a[@class="PageLink"]'
    xpath_shop_list = r'//div[@id="shop-all-list"]/ul/li'
    xpath_shop_title = r'./div[@class="txt"]/div[@class="tit"]/a'
    xpath_comment = r'./div[@class="txt"]/div[@class="comment"]'
    xpath_tag = r'./div[@class="txt"]/div[@class="tag-addr"]'
    xpath_link_css = r'//link[@type="text/css"]/@href'

    urls = {
        # 字段说明: collection_name : [ url, page, page_type, useFont]
        'city_list': ['http://www.dianping.com/ajax/citylist/getAllDomesticProvince', 1, 'api', False],  # 城市列表,根据城市列表搜索各地美食
        'city_list': ['http://www.dianping.com/citylist', 1, 'api', False],  # 城市列表,根据城市列表搜索各地美食
    }

    def __init__(self, headers=None, proxies=None, retries=3, timeout=10):
        '''
        创建Session信息
        '''
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.host = 'https://www.dianping.com/'
        self.timeout = timeout
        self.headers = headers
        if self.headers is None:
            self.headers = self.get_headers()

        self.proxies = proxies
        if self.proxies is None:
            self.proxies = get_proxy()

        try:
            resp = self.session.get(self.host, headers=self.headers, proxies=self.proxies, timeout=self.timeout)
            print(resp.status_code, resp.url, self.host)
            if resp.url != self.host:
                raise Exception(f"被重定向到 {resp.url} ,可能出现验证码问题!请重新尝试!")
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
            'Referer': 'https://www.dianping.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,zh-TW;q=0.5'
        }

    def get_cookies(self):
        '''
        返回默认cookies
        '''
        return '_lxsdk_cuid=173b45bd0a4c8-0a9fa9c8e8f771-39770e5a-1f7442-173b45bd0a5c8; _lxsdk=173b45bd0a4c8-0a9fa9c8e8f771-39770e5a-1f7442-173b45bd0a5c8; _hc.v=6b7ff5b3-36e2-8709-45ba-cdbf81efceb7.1596458783; fspop=test; Hm_lvt_602b80cf8079ae6591966cc70a3940e7=1596459039; s_ViewType=10; cy=2; cye=beijing; _lxsdk_s=173b768f472-8cb-10b-0ef%7C%7C64; Hm_lpvt_602b80cf8079ae6591966cc70a3940e7=1596510985'

    def get_ajax_headers(self):
        '''
        返回调用Ajax接口的Header
        '''
        return {
            'Upgrade-Insecure-Requests': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'User-Agent': 'Mozilla/5.0 (Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
            'Origin': 'http://www.dianping.com',
            'Referer': 'http://www.dianping.com/citylist',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,zh-TW;q=0.5',
        }

    def replace_font(self, map_data, replace_str):
        '''
        字体编码替换
        '''
        replace_str = re.sub('\s', '', replace_str.replace('uni', '&#'))  # 去掉空白符，还原 `&#`符号信息用来匹配字典
        for idx in re.findall(r'&#x....;', replace_str):
            rep_val = map_data.get(idx)
            if rep_val is None:
                print('没有匹配的idx:[' + idx + ']')
                continue
            replace_str = replace_str.replace(idx, rep_val)
        return replace_str

    def get_prov_list(self):
        '''
        获取城市名称
        '''
        province_list = []
        prov_url = "http://www.dianping.com/ajax/citylist/getAllDomesticProvince"
        try:
            # 访问省份列表 #
            resp = self.session.post(prov_url, proxies=self.proxies, timeout=self.timeout, headers=self.get_ajax_headers())
            logging.info(f'prov_url:{prov_url}, cur_url:{resp.url}')
            if resp.status_code != 200:
                # 可能出现验证码，退出 #
                logging.info(f"{prov_url} : 可能出现验证码情况，请重新尝试!")
                return None
            province_list = resp.json().get('provinceList')
            if province_list is None:
                logging.error(f'没有成功获取省份列表信息!实际获取信息如下：{resp.text}')
                return None
            for prov in province_list:
                prov['_id'] = prov['provinceId']
        except requests.exceptions.ProxyError as e:
            logging.error('proxy_error ' + str(e))
        except Exception as e:
            logging.error('proxy: ' + str(e))
        return province_list

    def get_city_list(self, prov):
        '''
        获取城市名称
        params:
            prov: 省份信息字典 : 示例 {areaId: 1 , provinceId: "1" , provinceName: "北京"}
        '''
        if prov is None:
            logging.error(f'param "prov" is None or not a dict type: [{prov}]')
            return None
        city_url = "http://www.dianping.com/ajax/citylist/getDomesticCityByProvince"
        payload = dict()
        payload["provinceId"] = int(prov['provinceId'])
        city_list = {}
        try:
            # 获取省份对应的地区列表 #
            resp = self.session.post(city_url, json=payload, proxies=self.proxies, timeout=self.timeout, headers=self.get_ajax_headers())
            print(city_url, resp.url)
            logging.info(f'status_code:{resp.status_code}, prov: {prov["provinceName"]}, city_url:{city_url}, cur_url:{resp.url}')
            if resp.status_code != 200:
                # 可能出现验证码，退出 #
                logging.info(f"{city_url} : 可能出现验证码情况，请重新尝试!, \nstatus:{resp.status_code}, 信息内容如下:\n{resp.text[0:100]}")
                return None
            city_list = resp.json()
            if city_list is None:
                logging.error(f'没有成功获取【地区】列表信息!实际获取信息如下：{resp.text}')
                return None
            city_list = city_list.get('cityList')
            for city in city_list:
                city['_id'] = city['cityId']
        except requests.exceptions.ProxyError as e:
            logging.error('proxy_error ' + str(e))
        except Exception as e:
            logging.error('proxy: ' + str(e))
        return city_list

    def get_nav_list(self, city):
        '''
        获取频道导航链接列表- 例如美食、生活等频道信息
        params:
            city: 城市信息字典 : 示例 beijing
        '''
        if city is None:
            logging.error(f'param "city" is None or not a dict type: [{city}]')
            return None
        city_url = "http://www.dianping.com/" + city + "/ch0"
        nav_list = {}
        try:
            # 获取地区对应的频道列表 #
            resp = self.session.get(city_url, proxies=self.proxies, timeout=self.timeout, headers=self.get_headers())
            print(city_url, resp.url)
            logging.info(f'status_code:{resp.status_code}, city_url:{city_url}, cur_url:{resp.url}')
            if resp.status_code != 200:
                # 可能出现验证码，退出 #
                logging.info(f"{city_url} : 可能出现验证码情况，请重新尝试!, \nstatus:{resp.status_code}, 信息内容如下:\n{resp.text[0:100]}")
                return None
            doc = etree.HTML(resp.text)
            # 1. 找到CSS文件地址，并读取内容找到字体woff文件
            nc_item = doc.xpath(self.xpath_nav)
            for item in nc_item:
                href = item.xpath('./@href')[0]
                title = item.xpath('string(.)')
                # print(title, href)
                nav_list[title] = href
        except requests.exceptions.ProxyError as e:
            logging.error('proxy_error ' + str(e))
        except Exception as e:
            logging.error('proxy: ' + str(e))
        return nav_list

    def get_shop_list(self, city_ch_url):
        '''
        获取频道导航链接列表- 例如美食、生活等频道信息
        params:
            city_ch_url: 城市频道URL地址
        '''
        if city_ch_url is None:
            logging.error(f'param "city_ch_url" is None or not a dict type: [{city_ch_url}]')
            return None
        url_list = [city_ch_url]
        shop_list = []
        max_page = 1   # 默认只有一页，第一次访问页面时会自动计算总页数
        is_cal = False  # 标记是否计算过最大页数，避免循环计算

        try:
            glyp_font = GlypFont(ptype='dianping')
            # key : reviewTag 评论区,address 店铺地址,
            #       tagName 店铺评价特点Tag,shopNum 人均消费数字
            # value: 字形编码与字符关系映射 dict
            glyp_map = {}
            proxies = self.proxies
            for city_url in url_list:
                # 获取地区对应的频道列表 #
                resp = self.session.get(city_url, proxies=proxies, timeout=self.timeout, headers=self.get_headers())
                print('src_url:' + city_url + ',real_url:' + resp.url)
                logging.info(f'status_code:{resp.status_code}, city_url:{city_url}, cur_url:{resp.url}')
                if resp.status_code != 200:
                    # 可能出现验证码，退出 #
                    logging.info(f"{city_url} : 可能出现验证码情况，请重新尝试!, \nstatus:{resp.status_code}, 信息内容如下:\n{resp.text[0:100]}")
                    return None
                resp_data = resp.text
                resp_data = resp_data.replace('&#', 'uni')  # 字符实体编号先转换处理一下，否则后面解析就会直接转义为错误的字符#
                doc = etree.HTML(resp_data)
                link_css = doc.xpath(self.xpath_link_css)
                css_file = None
                for css in link_css:
                    if css.startswith(r'//s3plus.meituan.net'):
                        css_file = 'http:' + css
                        break
                if css_file is not None:
                    resp = self.session.get(css_file, proxies=self.proxies, timeout=self.timeout, headers=self.get_headers())
                    # 提取 font_family 与 font_url 列表
                    font_list = re.findall(r'(?<=font-family: \")(.*)?(?=\"\;).*?(?<=,url\(\")(//s3plus.*?\.woff).*?(?<=font-family: \")(.*)?(?=\"\;).*?(?<=,url\(\")(//s3plus.*?\.woff).*?(?<=font-family: \")(.*)?(?=\"\;).*?(?<=,url\(\")(//s3plus.*?\.woff).*?(?<=font-family: \")(.*)?(?=\"\;).*?(?<=,url\(\")(//s3plus.*?\.woff).*?', resp.text)
                    font_list = list(font_list[0])
                    font_dict = {}  # 按照字体名称区分不同字体文件,字体名称后续
                    for i in range(0, len(font_list), 2):
                        k = font_list[i].split('-')[-1]
                        v = 'http:' + font_list[i+1]
                        font_dict[k] = v
                        glyp_map[k] = glyp_font.getFont(v)

                # 提取Shop信息
                item_list = doc.xpath(self.xpath_shop_list)
                # print('shop_num:', len(item_list))
                for shop in item_list:
                    item = {}
                    shop_title = shop.xpath(self.xpath_shop_title + '/h4')[0].xpath('string(.)').strip()
                    shop_link = shop.xpath(self.xpath_shop_title)[0].xpath('./@href')[0]
                    shop_id = shop_link.split('/')[-1]
                    shop_tags = shop.xpath(self.xpath_tag)[0].xpath('./a')[0].xpath('string(.)')
                    shop_addr = shop.xpath(self.xpath_tag)[0].xpath('./span[@class="addr"]')[0].xpath('string(.)')
                    shop_comm = shop.xpath(self.xpath_comment)[0].xpath('string(.)')
                    shop_tags = self.replace_font(glyp_map['tagName'], shop_tags)
                    shop_addr = self.replace_font(glyp_map['address'], shop_addr)
                    shop_comm = self.replace_font(glyp_map['shopNum'], shop_comm)
                    # 获取所有信息，保存到字典中
                    item['_id'] = shop_id
                    item['title'] = shop_title
                    item['link'] = shop_link
                    item['tags'] = shop_tags
                    item['addr'] = shop_addr
                    item['comment'] = shop_comm.split('|')[0]
                    item['price'] = shop_comm.split('|')[1]
                    shop_list.append(item)
                    print(shop_id, shop_link, shop_title, shop_addr, shop_comm, shop_tags)
                    time.sleep(3)

                # 计算页面总页数
                if is_cal is False:
                    page_links = doc.xpath(self.xpath_page_num)
                    for item in page_links:
                        num = int(item.xpath('string(.)'))
                        if num > max_page:
                            max_page = num
                    if max_page > 1:
                        is_cal = True
                        for pn in range(2, max_page):
                            url_list.append(city_ch_url + '/p' + str(pn))
                            # print(city_ch_url + '/p' + str(pn))
                        # debug
                        # break
        except requests.exceptions.ProxyError as e:
            logging.error('proxy_error ' + str(e))
        except Exception as e:
            logging.error('proxy: ' + str(e))
            traceback.print_exc()
        return shop_list

    def get_shop_url_list(self, city_ch_url):
        '''
        获取频道导航链接URL列表- 例如美食、生活等频道信息
        params:
            city_ch_url: 城市频道URL地址
        '''
        if city_ch_url is None:
            logging.error(f'param "city_ch_url" is None or not a dict type: [{city_ch_url}]')
            return None
        url_list = [city_ch_url]
        max_page = 0
        try:
            proxies = self.proxies
            # 获取地区对应的频道列表 #
            resp = self.session.get(city_ch_url, proxies=proxies, timeout=self.timeout, headers=self.get_headers())
            print('src_url:' + city_ch_url + ',real_url:' + resp.url)
            logging.info(f'status_code:{resp.status_code}, src_url:{city_ch_url}, cur_url:{resp.url}')
            if resp.status_code != 200:
                # 可能出现验证码，退出 #
                logging.info(f"{city_ch_url} : 可能出现验证码情况，请重新尝试!, \nstatus:{resp.status_code}, 信息内容如下:\n{resp.title}")
                return None
            resp_data = resp.text
            doc = etree.HTML(resp_data)
            # 计算页面总页数
            page_links = doc.xpath(self.xpath_page_num)
            for item in page_links:
                num = int(item.xpath('string(.)'))
                if num > max_page:
                    max_page = num
            if max_page > 1:
                for pn in range(2, max_page):
                    url_list.append(city_ch_url + '/p' + str(pn))
        except requests.exceptions.ProxyError as e:
            logging.error('proxy_error ' + str(e))
        except Exception as e:
            logging.error('proxy: ' + str(e))
            traceback.print_exc()
        return url_list

    def get_shop_review(self, city_id, shop_id):
        '''
        获取评论信息
        params:
            city_id: 城市ID
            shop_id: 商铺ID
        '''
        # TODO 获取评论信息,需要Cookie信息
        token_str = '&tcv=912etv6bvu&_token=eJxVT11vgkAQ%2FC%2F72gvcySHCm4bSgKeJfKjV%2BICCSEABOYva9L93SexDk01mdnZms%2FsNVzcBi1FKOSPwlV7BAqZQZQgEZIsT3RzqJteYRvmAwOG%2FppkGgf11aYO1ZdQYEZMPd73io7BlJuMEZWNHeq73fLQjA47Vu1w0wUnK2lLVruuUJI8vdX7JlEN1VttTVasFT2623dTClFlWHu94FGDyHGISsXhh%2FEL518%2FwC%2FS2eXZBlnr3MGh52xz9WRtG97mzFoLWnti78hlJLzx8zQLK%2FOnIcEU3mW42t6IUDXcme77y4qJ%2BS4vlp%2B0sHpWIznRuJ8E00ObPd1yp%2Bt4z0h1a5sF6sKzij2a1Kr2iLDdRM16MH%2BnD9%2BHnFx1caKk%3D&uuid=6b7ff5b3-36e2-8709-45ba-cdbf81efceb7.1596458783&platform=1&partner=150&optimusCode=10&originUrl=http%3A%2F%2Fwww.dianping.com%2Fshop%2Fk4duDDqpL9tgglfx'
        comm_url = f'http://www.dianping.com/ajax/json/shopDynamic/allReview?shopId={shop_id}&cityId={city_id}&shopType=10{token_str}'
        try:
            headers = self.get_ajax_headers()
            headers['Referer'] = 'http://www.dianping.com/shop/' + shop_id
            resp = self.session.get(comm_url, proxies=self.proxies, timeout=self.timeout, headers=self.get_ajax_headers())
            print(resp.json())
        except requests.exceptions.ProxyError as e:
            logging.error('proxy_error ' + str(e))
        except Exception as e:
            logging.error('proxy: ' + str(e))
        pass

    def fetch_all(self):
        '''
        爬取所有页面数据,并且输出到JSON文件中
        '''
        try:
            import db_mongo as db
            mongo = db.MongoDb(**db.default_config)
            prov_list = self.get_prov_list()
            logging.info('prov_list 入库, 记录数:' + str(len(prov_list)))
            mongo.change_collection('dianping_prov_list')
            mongo.upsert(prov_list)
            urls = []
            for prov in prov_list:
                city_list = self.get_city_list(prov)
                logging.info('city_list 入库, 记录数:' + str(len(city_list)))
                mongo.change_collection('dianping_city_list')
                mongo.upsert(city_list)
                for city in city_list:
                    city_py_name = city['cityPyName']
                    ch_url = "http://www.dianping.com/" + city_py_name + "/ch0"
                    shop_list = self.get_shop_url_list(ch_url)
                    logging.info('shop_list 入库, 记录数:' + str(len(shop_list)))
                    mongo.change_collection('dianping_shop_list')
                    mongo.upsert(shop_list)
            # 访问URL列表入库
            # mongo.change_collection('url_queue_dianping')
            # mongo.insert_many(urls)
            print(urls)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    try:
        dianping = Dianping()
        dianping.get_shop_list('http://www.dianping.com/nanjing/ch0')
    except Exception as e:
        print(e)
