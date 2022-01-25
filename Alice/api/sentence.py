from time import time
from datetime import datetime
from webbrowser import get
import aiohttp
import random
import asyncio
import requests
from pprint import pprint
from baiduspider import BaiduSpider
from dtanys import jsonpath
from lxml import etree
import os

async def oneYan():
    '''一言'''
    a1 = range(97,109)
    b1 = random.choice([chr(i) for i in a1])
    data = {
        'c':b1,
        'encode':'text',
        'charset':'utf-8',
        'max_length':100,
    }
    url = "https://v1.hitokoto.cn"
    async with aiohttp.request("GET", url, params = data) as r:
        return await r.text()

async def translation(string):
    '''翻译'''
    data = {
        'doctype': 'json',
        'type': 'AUTO',
        'i': string
    }
    url = "http://fanyi.youdao.com/translate"
    async with aiohttp.request('GET', url, params = data) as r:
        res = await r.json(content_type=None)
    res = jsonpath.xpath(res,'/*tgt')
    return ''.join(res)

def getBaike(text):
    '''百科'''
    spider = BaiduSpider()
    try:
        res = jsonpath.xpath(spider.search_baike(query=text).plain, '//["des","title","url"]//[0:1]')
    except Exception as e:
        spider = BaiduSpider()
        res = spider.search_web(query=text, exclude=['news', 'video', 'tieba', 'blog', 'gitee', 'related', 'calc', 'music'])
        res = jsonpath.xpath(res, '[0]/result["des","title","url"]')
    return res[1] + '\n' + res[0] + '\n' + res[2].replace('https://baike.baidu.com','')

def getBlog(text):
    '''博客'''
    spider = BaiduSpider()
    res = jsonpath.xpath(spider.search_web(query=text, exclude=['news', 'video', 'tieba', 'baike','gitee','related','calc', 'music']).plain, '//["des","title","url"]//[0:1]')
    return res[1] + '\n' + res[0] + '\n' + res[2]

def getMusic(text):
    '''音乐'''
    spider = BaiduSpider()
    res = jsonpath.xpath(spider.search_web(query=text, exclude=['news', 'video', 'tieba', 'baike', 'related','calc', 'blog', 'gitee']).plain, '//["des","title","url"]//[0:1]')
    return res[1] + '\n' + res[0] + '\n' + res[2]

def getwiki(text):
    res = requests.get(f'https://zh.wikipedia.org/zh-cn/{text}')
    html = etree.HTML(res.content)
    return ''.join(html.xpath("//div[@class='mw-parser-output']//p//text()")).strip()

async def getImage_seovx():
    '''图片'''
    url = "https://cdn.seovx.com/ha/?mom=302"
    async with aiohttp.request('GET', url) as r:
        res = await r.content.read()
    return res