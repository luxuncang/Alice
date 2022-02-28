from .download import bil_download, config
from dtanys import jsonpath
from pprint import pprint
import aiohttp
import requests

async def bil_search(word: str, order: str = "default"):
    '''
    排序方式
    #### 字段	说明
    - default	综合排序
    - pubdate	按发布日期倒序排序
    - senddate	按修改日期倒序排序
    - id	按投稿ID倒序排序
    - ranklevel	按相关度排序
    - click	按点击从高至低排序
    - scores	按评论数从高至低排序
    - damku	按弹幕数从高至低排序
    - stow	按收藏数从高至低排序
    '''
    url = 'https://api.bilibili.com/x/web-interface/search/type'
    # https://api.bilibili.com/x/web-interface/search/type?&page=1&order=click&keyword=MMD&search_type=video
    params = {
        'page': 1,
        'order': order,
        'keyword': word,
        'search_type': 'video',
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'Referer': 'https://search.bilibili.com'
    }
    requests.get(url)
    async with aiohttp.request('GET', url, params = params, headers = headers) as r:
            res = await r.json(content_type=None)
    return list(zip(*jsonpath.xpath(res, '//*["aid", "bvid", "arcurl", "tag", "author", "description", "pic"]')))

# if __name__ == '__main__':
#     print(asyncio.run(search("原神2.5")))
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(search('原神2.5'))