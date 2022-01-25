from urllib import parse
from playwright.async_api import Playwright, async_playwright
import asyncio
from pprint import pprint

async def cloudmusic(text):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        # browser = await playwright.firefox.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(f'https://music.163.com/#/search/m/?s={parse.quote(text)}')
        iframe =  page.frame_locator("#g_iframe").locator(".srchsongst > div:nth-child(1) > div.td.w0 > div > div > a:nth-child(1)")
        url = await iframe.get_attribute('href')
        await page.goto(f"https://music.163.com{url}")
        iframe = page.frame_locator("#g_iframe").locator("div.u-cover.u-cover-6.f-fl > img")
        imgurl = await iframe.get_attribute('src')
        iframe = page.frame_locator("#g_iframe").locator("em.f-ff2")
        title = await iframe.inner_text()
        iframe = page.frame_locator("#g_iframe").locator("div.m-lycifo > div.f-cb > div.cnt > p:nth-child(2) > span")
        summary = await iframe.get_attribute('title')
        await page.frame_locator("#g_iframe").locator("#flag_ctrl").click()
        iframe = page.frame_locator("#g_iframe").locator("#lyric-content")
        lyric = await iframe.inner_text()

        await browser.close()
        
        return {'title':title, 'summary':summary, 'pictureUrl':imgurl, 'jumpUrl': f"https://music.163.com{url}", 'musicUrl':f'http://music.163.com/song/media/outer/url?{url[6:]}', 'brief': f'[Alice Music] {title}'}, lyric[:-1]
