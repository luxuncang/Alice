import aiohttp
import asyncio

async def qingyunke_chat(text):
    '''青客云机器人'''

    url = "http://api.qingyunke.com/api.php"
    data = {
        'key':'free',
        'appid':0,
        'msg':text,
    }
    async with aiohttp.request("GET", url, params = data) as r:
        res = await r.json(content_type=None)
        res = res['content'].replace("{br}",'\n').replace('★','').split('\n')
        ress = ''
        for i in res:
            ress +=i.strip()+'\n'
        return ress.rstrip('\n').replace('菲菲','墨墨')
