# -*- coding:utf-8 -*-
"""
@author: XiangNan
@desc: 使用百度翻译进行中英文互译，仅支持中英文互译
"""
import re
import json
import execjs
import requests


class BaiduTranslate:
    def __init__(self, word):
        self.word = word
        self.session = requests.session()
        self.start_url = 'https://fanyi.baidu.com/'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
            'referer': self.start_url
        }

    def get_sign(self, gtk):
        """
        获取翻译请求所需的参数sign
        """
        # index.js为从百度翻译网页扒下来的获取sign的JavaScript代码
        # 好多行，我就懒得用Python实现了，直接扒下来
        try:
            with open('index.js') as f:
                js_data = f.read()
            ctx = execjs.compile(js_data)
            sign = ctx.call('e', self.word, gtk)
            return sign
        except:
            return '获取sign参数出错'

    def get_token(self, response):
        """
        获取翻译请求所需的token及gtk参数
        """
        # token、gtk参数在百度翻译首页直接返回，此处正则匹配获取
        try:
            token = re.findall(r"token: '(.*?)',", response, re.S)
            gtk = re.findall(r"window.gtk = '(.*?)';", response, re.S)
            if token and gtk:
                return token[0], gtk[0]
        except:
            return '获取token或gtk参数出错'

    def get_response(self):
        """
        请求两次百度翻译首页，并返回第二次的源代码
        """
        response_first = self.session.get(self.start_url)
        response_second = self.session.get(self.start_url)
        return response_second.text

    def translate(self):
        """
        拼接翻译请求所需的参数，发送请求并返回翻译结果
        """
        response = self.get_response()
        token, gtk = self.get_token(response)
        sign = self.get_sign(gtk)
        if u'\u4e00' <= self.word <= u'\u9fa5':
            from_, to_ = 'zh', 'en'
        elif (u'\u0041' <= self.word <= u'\u005a') or (u'\u0061' <= self.word <= u'\u007a'):
            from_, to_ = 'en', 'zh'
        else:
            return '仅支持中英互译，请重新输入'
        # POST请求参数
        data = {
            'from': from_,
            'to': to_,
            'query': self.word,
            'transtype': 'translang',
            'simple_means_flag': '3',
            'sign': sign,
            'token': token
        }
        # 翻译请求网址
        trans_url = 'https://fanyi.baidu.com/v2transapi'
        # 发送请求
        res = self.session.post(url=trans_url, data=data, headers=self.headers)
        # 获取翻译结果
        json_data = json.loads(res.text)
        result = json_data['trans_result']['data'][0]['dst']
        return result


if __name__ == '__main__':
    # 所要翻译的单词
    word = 'blue'
    # 翻译并输出结果
    translator = BaiduTranslate(word)
    result = translator.translate()
    print(result)