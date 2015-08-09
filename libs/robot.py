#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Robot. Just text response.
Using API from http://www.tuling123.com/openapi/cloud/access_api.jsp
"""

import requests
from tornado.options import options

#  import urllib
#  from tornado.httpclient import AsyncHTTPClient
#  AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')
#  def gen_url(msg, userid, key=options.robot_key, baseurl=options.robot_url):
#      query = urllib.urlencode({'key': key, 'userid': userid, 'info': msg})
#      return '{0}?{1}'.format(baseurl, query)


def get(msg, userid, key=options.robot_key, url=options.robot_url):
    query = {'key': key, 'userid': userid, 'info': msg}
    response = requests.get(url, params=query)
    return parse_response(response)


def parse_response(response):
    if response.status_code != 200:
        return u'机器人开小差了...'
    r = response.json()
    if r['code'] == 100000:  # text
        return r['text']
    elif r['code'] == 305000:  # train
        return '列车查询请上12306.cn'
    elif r['code'] == 306000:  # flight
        return '航班？遗嘱写好了没？'
    elif r['code'] == 200000:  # picture
        return '现在图片满天飞，你...'
    elif r['code'] == 302000:  # news
        return '看新闻请...对不起...'
    elif r['code'] == 308000:  # recipe,video,book
        return '就知道你是伸手党...'
    elif r['code'] == 40001:  # key length error
        return '这傻X开发者...我竟无言以对!!!'
    elif r['code'] == 40002:  # empty content
        return '你磨磨叽叽些什么呢？'
    elif r['code'] == 40003:  # key or account error
        return '这脑残开发者...我竟无言以对!!!'
    elif r['code'] == 40004:  # query limit
        return '我屮艸芔茻，你们要不要这么寂寞，洗洗睡吧！！！'
    elif r['code'] == 40005:  # function not support
        return '你挫到我的痛处了...'
    elif r['code'] == 40006:  # server upgrade
        return '别理我，让我休息会...'
    elif r['code'] == 40007:  # server data format error
        return '烫烫烫烫...'
