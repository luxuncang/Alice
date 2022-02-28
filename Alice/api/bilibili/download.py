from importlib.resources import path
from ...internaltype import config
from bilibili_api import video, Credential, platform
import aiohttp
import os, asyncio, time
from bilibili_api import bangumi
from urllib.parse import urlparse
if 'windows' in platform.system().lower():
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from .avtobv import Encode

SESSDATA = config['ApiKey']['Bilibili']['sessdata']
BILI_JCT = config['ApiKey']['Bilibili']['bili_jct']
BUVID3 = config['ApiKey']['Bilibili']['buvid3']

# FFMPEG 路径，查看：http://ffmpeg.org/

FFMPEG_PATH = "ffmpeg"

async def url_to_bvid(url: str):
    res = urlparse(url)
    path = os.path.split(res.path)[-1]
    if path[:2] == 'BV':
        return path
    elif path[:2] == 'ep':
        path = await bangumi.get_episode_info(path[2:])
        return path['epInfo']['bvid']
    elif path[:2] == 'av':
        path = Encode(path[2:])
        return path
    return None

async def bil_download(video_id: str):
    # 实例化 Credential 类
    video_id = await url_to_bvid(video_id)
    credential = Credential(sessdata=SESSDATA, bili_jct=BILI_JCT, buvid3=BUVID3)
    # 实例化 Video 类
    v = video.Video(bvid = video_id, credential=credential)
    # 获取视频下载链接
    url = await v.get_download_url(0)
    # 视频轨链接
    video_url = url["dash"]["video"][0]['baseUrl']
    # 音频轨链接
    audio_url = url["dash"]["audio"][0]['baseUrl']
    HEADERS = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.bilibili.com/"
    }
    async with aiohttp.ClientSession() as sess:
        # 下载视频流
        async with sess.get(video_url, headers=HEADERS) as resp:
            length = resp.headers.get('content-length')
            with open('video_temp.m4s', 'wb') as f:
                process = 0
                while True:
                    chunk = await resp.content.read(1024000)
                    if not chunk:
                        break

                    process += len(chunk)
                    # print(f'下载视频流 {process} / {length}')
                    f.write(chunk)

        # 下载音频流
        async with sess.get(audio_url, headers=HEADERS) as resp:
            length = resp.headers.get('content-length')
            with open('audio_temp.m4s', 'wb') as f:
                process = 0
                while True:
                    chunk = await resp.content.read(1024000)
                    if not chunk:
                        break

                    process += len(chunk)
                    # print(f'下载音频流 {process} / {length}')
                    f.write(chunk)
        path = str(time.time())
        # 混流
        print('混流中')
        os.system(f'{FFMPEG_PATH} -i video_temp.m4s -i audio_temp.m4s -vcodec copy -acodec copy ./downloads/{path}.mp4')

        # 删除临时文件
        os.remove("video_temp.m4s")
        os.remove("audio_temp.m4s")

        return f'./downloads/{path}.mp4', video_id
