import aiofiles
import os
import aiohttp

async def ftp(path: str):
    try:
        async with aiofiles.open(path, 'rb') as f:
            res = await f.read()
            return {'file': (res, os.path.split(path)[1])}
    except FileNotFoundError:
        return '文件不存在!'

async def ftp_file(path, name, url):
    async with aiohttp.request('GET', url) as r:
        dates = await r.content.read()
    if not os.path.exists(path):
        os.makedirs(path)
    async with aiofiles.open(os.path.join(path, name), 'wb') as f:
        res = await f.write(dates)
        return res
