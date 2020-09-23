from os import path, makedirs, remove
import re
import requests
import time
import numpy as np
from fontTools.ttLib import TTFont
import json


# 使用OCR识别出来的字形对应文字含义列表
font_str_order_dianping = '''
1234567890店中美家馆小
车大市公酒行国品发电金心业商司超生
装园场食有新限天面工服海华水房饰城
乐汽香部利子老艺花专东肉菜学福饭人
百餐茶务通味所山区门药银农龙停尚安
广鑫一容动南具源兴鲜记时机烤文康信
果阳理锅宝达地儿衣特产西批坊州牛佳
化五米修爱北养卖建材三会鸡室红站德
王光名丽油院堂烧江社合星货型村自科
快便日民营和活童明器烟育宾精屋经居
庄石顺林尔县手厅销用好客火雅盛体旅
之鞋辣作粉包楼校鱼平彩上吧保永万物
教吃设医正造丰健点汤网庆技斯洗料配
汇木缘加麻联卫川泰色世方寓风幼羊烫
来高厂兰阿贝皮全女拉成云维贸道术运
都口博河瑞宏京际路祥青镇厨培力惠连
马鸿钢训影甲助窗布富牌头四多妆吉苑
沙恒隆春干饼氏里二管诚制售嘉长轩杂
副清计黄讯太鸭号街交与叉附近层旁对
巷栋环省桥湖段乡厦府铺内侧元购前幢
滨处向座下县凤港开关景泉塘放昌线湾
政步宁解白田町溪十八古双胜本单同九
迎第台玉锦底后七斜期武岭松角纪朝峰
六振珠局岗洲横边济井办汉代临弄团外
塔杨铁浦字年岛陵原梅进荣友虹央桂沿
事津凯莲丁秀柳集紫旗张谷的是不了很
还个也这我就在以可到错没去过感次要
比觉看得说常真们但最喜哈么别位能较
境非为欢然他挺着价那意种想出员两推
做排实分间甜度起满给热完格荐喝等其
再几只现朋候样直而买于般豆量选奶打
每评少算又因情找些份置适什蛋师气你
姐棒试总定啊足级整带虾如态且尝主话
强当更板知己无酸让入啦式笑赞片謠差
像提队走嫩才刚午接重串回晚微周值费
性桌拍跟块调糕
'''
font_dict_info = {
    'dianping': {
        'font_str': font_str_order_dianping,
        'font_file': 'dianping.woff'
    },
    'maoyan': {
        'font_str': '0926731845',
        'font_file': 'maoyan.woff'
    },
}


class GlypFont():
    '''
    字体解析处理对象
    对外提供方法:
        parseContent(response.text)
    '''
    def __init__(self, ptype, font_path="./font/"):
        '''
        初始化基准字体文件的 字形与字符关系映射表
        '''
        try:
            self.ptype = ptype
            base_font_file = font_dict_info[ptype]['font_file']
            font_order = font_dict_info[ptype]['font_str']
            # 字符列表
            self.write_path = font_path
            self.base_ch_list = [ch for ch in font_order.replace('\n', '')]
            base_font = TTFont(self.write_path + base_font_file)
            # 字形编号列表
            self.base_glyh_list = base_font.getGlyphOrder()[2:]
            # 字形坐标轮廓列表
            self.base_axis_list = self.getAxis(base_font)
            self.base_font_dict = {}
            print('字形数量:' + str(len(self.base_glyh_list)) +
                  ',字符数量:' + str(len(self.base_ch_list)))
            if len(self.base_glyh_list) != len(self.base_ch_list):
                raise Exception("字体关系映射对应不上呀!")
            # 构建基准 `字符` 与 `字形` 映射字典
            for i in range(len(self.base_ch_list)):
                k = self.base_glyh_list[i]
                v = self.base_ch_list[i]
                self.base_font_dict[k] = v
        except Exception as e:
            print(e)

    def getAxis(self, font):
        '''
        获取TTFont字体坐标
        '''
        glyp_list = font.getGlyphOrder()[2:]
        font_axis = []
        for uni in glyp_list:
            axis = []
            for i in font['glyf'][uni].coordinates:
                axis.append(i)
            font_axis.append(axis)
        return font_axis

    def getFont(self, font_url):
        '''
        下载新字体文件
        param:
            font_url: http*.woff
        '''
        if font_url is not None and font_url.rsplit('.', maxsplit=1)[1] == 'woff':
            font_file = self.write_path + font_url.split('/')[-1]
            # 文件已经存在，只需要读取JSON字典就可以了
            json_file = font_file.rsplit('.', maxsplit=1)[0] + '.json'
            if path.exists(json_file):
                # json 映射文件已经保存过
                data = []
                with open(json_file, 'r') as f:
                    data = f.read()
                return json.loads(data)  # 每个JSON文件只保存了一个字典
            else:
                try:
                    print('开始下载字体文件: ' + font_url)
                    file_content = requests.get(font_url).content
                    if not path.exists(self.write_path):
                        makedirs(self.write_path)
                    with open(font_file, 'wb') as f:
                        f.write(file_content)

                    print('解析字体文件: ' + font_file)
                    jsdata = self.parseFont(font_file)
                    if self.ptype == 'maoyan':
                        remove(font_file)
                    else:
                        print('保存字体文件:' + json_file)
                        with open(json_file, 'w') as f:
                            f.write(json.dumps(jsdata, ensure_ascii=False))
                    return jsdata
                except Exception as e:
                    print(f'字体URL地址: {font_url} 错误!error:{str(e)}')
        return None

    def parseFont(self, font_file):
        '''
        获取当前页面动态字体的字典
        '''
        cur_font = TTFont(font_file)
        uni_list = cur_font.getGlyphOrder()[2:]
        cur_axis = self.getAxis(cur_font)
        font_dict = {}
        for i in range(len(uni_list)):
            min_avg, uni = 99999, None
            for j in range(len(self.base_glyh_list)):
                avg = self.compare_axis(cur_axis[i], self.base_axis_list[j])
                if avg < min_avg:
                    min_avg = avg
                    uni = self.base_glyh_list[j]
            font_dict['&#x' + uni_list[i][3:].lower() + ';'] = self.base_font_dict[uni]
        return font_dict

    def compare_axis(self, axis1, axis2):
        '''
        使用欧式距离计算
        '''
        if len(axis1) < len(axis2):
            axis1.extend([0, 0] for _ in range(len(axis2) - len(axis1)))
        elif len(axis2) < len(axis1):
            axis2.extend([0, 0] for _ in range(len(axis1) - len(axis2)))
        axis1 = np.array(axis1)
        axis2 = np.array(axis2)
        return np.sqrt(np.sum(np.square(axis1-axis2)))
