#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
# Author: zioer
# mail: xiaoyu0720@gmail.com
# Created Time: 2020年08月08日 星期六 23时20分26秒
# Brief:
################################################################################
import re
from urllib import parse
import requests


prefix = 'amemv.com/aweme/v[0-9]/feed'
url_re = re.compile(prefix)
video_re = re.compile('https://aweme-hl.*?/play/.*?FEED')


chunk_size = 4096*2
write_path = '/data/video/douyin/'
downloaded = {}   # 记录下载过的 video_id ，过滤重复下载地址
headers = {
    'user-agent': 'com.ss.android.ugc.aweme/120201 (Linux; U; Android 5.1.1; zh_CN; SM801; Build/LMY47V; Cronet/TTNetVersion:707ae96e 2020-07-28 QuicVersion:7aee791b 2020-06-05)'
}


def download_video(url, ratio='720p'):
    '''
    下载视频文件
    参数:
        url : 视频地址
        name: 视频中文名称
        ratio: 分辨率
    '''
    qs = url.split('?')
    if len(qs) != 2:
        return None
    else:
        # url参数解析
        query_str = qs[1].replace(r'\\u0026', '&')
        qlist = parse.parse_qs(query_str)
        video_id = qlist.get('video_id')
        if video_id is None:
            return None
        vid = video_id[0]
        if downloaded.get(vid) is None:
            downloaded[vid] = True
            filename = write_path + vid + '.mp4'
            print(f'正在下载 {filename} ...', end=' ')
            resp = requests.get(url, headers=headers, stream=True)
            with open(filename, 'wb') as fd:
                for chunk in resp.iter_content(chunk_size):
                    fd.write(chunk)
                fd.flush()
            print(" 下载完成!")
            return True


def response(flow):
    '''
    处理解析视频下载链接
    '''
    match = url_re.search(flow.request.url)
    if match:
        resp = flow.response
        data = str(resp.content)
        videos = re.findall(video_re, data)
        count = 0
        for item_url in videos:
            ret = download_video(item_url)
            if ret:
                count += 1
        print(f"{'-'*80}\n下载链接[ {flow.request.url} ]\n共下载视频 {count} 条.\n{'-'*80}")
