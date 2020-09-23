#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年07月20日 星期一 17时24分01秒
# Brief:
################################################################################
import scrapy


class BlogSpider(scrapy.Spider):
    name = 'blog'
    start_urls = [
        'https://vlikework.github.io',
    ]

    def parse(self, response):
        for quote in response.xpath('//*[@id="post"]'):
            yield {
                'title': quote.xpath('a/@title').get(),
                'link': response.url + quote.xpath('a/@href').get(),
            }
