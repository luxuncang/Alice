# # 百度api key

from dtanys import jsonpath
import aiohttp

from aiohttp.client import ClientSession
from ...internaltype import config

APIKEY = config['ApiKey']['Baidu']['APIKEY']
SECRETKEY = config['ApiKey']['Baidu']['SECRETKEY']


async def GetAccessToeken():
    token_host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={ak}&client_secret={sk}'.format(ak=APIKEY, sk=SECRETKEY)
    header = {'Content-Type': 'application/json; charset=UTF-8'}
    async with aiohttp.request('POST', token_host, headers = header) as r:
        result = await r.json(content_type=None)
    return result.get("access_token")


'''
通用文字识别（高精度版）
'''
async def baidu_ORC(images):
    urls = [i.url for i in images]
    res = []

    async with aiohttp.ClientSession() as session:
        access_token = await GetAccessToeken()
        for i in urls:
            header = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {
                'url': i,
            }
            params = {
                'access_token': access_token
            }
            async with session.post('https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic', params = params, data = data, headers = header) as r:
                res.append(await r.json(content_type=None))
    return '\n'.join(['\n'.join(jsonpath.xpath(i['words_result'], "//*words")) for i in res])
