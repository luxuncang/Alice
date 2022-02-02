import asyncio
import json
import os
from playwright.async_api import Playwright, async_playwright
from lxml import etree

def wrap(text: str, width: int = 18) -> str:
    '''
    文本换行
    '''
    res = ''
    for line in text.split('\n'):
        if len(line) <= width:
            res += '\n' + line
        else:
            res += '\n'
            while len(line) > width:
                res += line[:width] + '\n'
                line = line[width:]
            res += line
    return res

class Render:
    page = None

    @classmethod
    async def start(cls, headless = True):
        async with async_playwright() as playwright:
            cls.browser = await playwright.chromium.launch(headless = headless)
            cls.context = await cls.browser.new_context()
            Render.page = await cls.context.new_page()
            await Render.page.goto("file:///" + os.path.split(__file__)[0] + "/Render/index.html")
            while True:
                await asyncio.sleep(100)

    @classmethod
    async def close(cls):
        await cls.browser.close()
        await cls.context.close()

    @staticmethod
    async def render(text: str):
        text = wrap(text, width=150)
        while True:
            if Render.page:
                await Render.page.evaluate("([text]) => document.getElementById('pretext').innerText = text", [text])
                # await Render.page.evaluate_handle(f'var text = {text};\ndocument.getElementById("pretext").innerText = text;')
                return await Render.page.locator('.card').screenshot()
            else:
                # print("Render.page is None")
                await asyncio.sleep(1)


class Action:
    '''动作类'''
    ...
        

class Element:
    '''元素类'''
    ...

class ActionContext(Action):
    '''新建context类'''
    def __init__(self, name) -> None:
        self.name = name

class ActionGoto(Action):
    '''跳转类'''
    def __init__(self, url: str, wait: float = 0) -> None:
        self.url = url
        self.wait = wait

class ActionClick(Action):
    '''点击类'''
    def __init__(self, selector, wait: float = 0) -> None:
        self.selector = selector
        self.wait = wait

class ActionLocator(Action):
    '''定位类'''
    def __init__(self, selector):
        self.selector = selector

class ActionLocatorScreenshot(Action):
    '''定位截图类'''
    def __init__(self, selector, path: str) -> None:
        self.selector = selector
        self.path = path

class ActionScreenshot(Action):
    '''截图类'''
    def __init__(self, path, full: bool = False) -> None:
        self.path = path
        self.full = full

class ActionFill(Action):
    '''填充类'''
    def __init__(self, selector, text):
        self.selector = selector
        self.text = text

class ActionPress(Action):
    '''按键类'''
    def __init__(self, selector, key, wait: float = 0):
        self.selector = selector
        self.key = key
        self.wait = wait

class ActionEvaluate(Action):
    '''脚本类'''
    def __init__(self, script, wait: float = 0):
        self.script = script
        self.wait = wait

class ActionMouse(Action):
    '''鼠标类'''
    def __init__(self, x, y, wait: float = 0):
        self.x = x
        self.y = y
        self.wait = wait

# 元素类
class ElementHtml(Element):
    '''html类'''
    def __init__(self, selector):
        self.selector = selector

class ElementText(Element):
    '''文本类'''
    def __init__(self, selector):
        self.selector = selector

class ElementRequest(Element):
    '''request类'''
    def __init__(self, n: int):
        self.n = n

class ElementResponse(Element):
    '''response类'''
    def __init__(self, n: int):
        self.n = n

class ElementConsole(Element):
    '''console类'''
    def __init__(self, n: int):
        self.n = n

class ElementXpath(Element):
    '''xpath类'''
    def __init__(self, selector):
        self.selector = selector

class ElementDownload(Element):
    '''下载类'''
    def __init__(self, selector):
        self.selector = selector

class ElementPdf(Element):
    '''pdf类'''
    def __init__(self, width: str, height: str):
        self.width = width
        self.height = height

async def get_elements_all(page, selector):
    html = await page.inner_html('html')
    h = etree.HTML(html)
    l = h.xpath("//" + selector)
    res = []
    for i in l:
        res.append(etree.tostring(i).decode('utf-8'))
    return '\n'.join(res)


class PlayExec:
    class Network:
        ...

    def __init__(self, playwright) -> None:
        self.playwright = playwright
        self.browser = None
        self.context = None
        self.page = None
        self.Network.request = []
        self.Network.response = []
        self.Network.console = []

    async def __aenter__(self):
        self.browser = await self.playwright.chromium.launch(headless=True, downloads_path='./downloads')
        self.context = await self.browser.new_context(accept_downloads=True, locale='zh-CN')
        self.context.on("page", self.handle_page)
        self.page = await self.context.new_page()
        self.network()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.context.close()
        await self.browser.close()

    async def play(self, action: Action) -> None:
        self.calltype = type(action)
        if isinstance(action, ActionGoto):
            await self.page.goto(action.url)
            await asyncio.sleep(action.wait)
        elif isinstance(action, ActionClick):
            await self.page.click(action.selector)
            await asyncio.sleep(action.wait)
        elif isinstance(action, ActionLocator):
            await self.page.click(action.selector)
        elif isinstance(action, ActionScreenshot):
            if action.path:
                return {'Image': await self.page.screenshot(action.path, full_page = action.full)}
            else:
                return {'Image': await self.page.screenshot(full_page = action.full)}
        elif isinstance(action, ActionFill):
            await self.page.fill(action.selector, action.text)
        elif isinstance(action, ActionPress):
            await self.page.press(action.selector, action.key)
            await asyncio.sleep(action.wait)
        elif isinstance(action, ActionEvaluate):
            await self.page.evaluate(action.script)
        elif isinstance(action, ActionLocatorScreenshot):
            if action.path:
                return {'Image': await self.page.locator(action.selector).screenshot(action.path)}
            else:
               return {'Image': await self.page.locator(action.selector).screenshot()}
        elif isinstance(action, ActionMouse):
            if action.x == 0 and action.y == 0:
                action.y = self.page.viewport_size['height']
            await self.page.mouse.wheel(action.x, action.y)
            await asyncio.sleep(action.wait)
        elif isinstance(action, ElementRequest):
            return {
                'Image': await Render.render(
                    json.dumps(
                        self.Network.request[-action.n:], 
                        ensure_ascii = False, 
                        indent = 4
                    )
                )
            }
        elif isinstance(action, ElementResponse):
            return {
                'Image': await Render.render(
                    json.dumps(
                        self.Network.response[-action.n:], 
                        ensure_ascii = False, 
                        indent = 4
                    )
                )
            }
        elif isinstance(action, ElementConsole):
            return {
                'Image': await Render.render(
                    '\n'.join(self.Network.console[-action.n:])
                )
            }

        elif isinstance(action, ElementHtml):
            return {
                'Image': await Render.render(
                    await self.page.inner_html(action.selector)
                )
            }
        elif isinstance(action, ElementText):
            return {
                'Image': await Render.render(
                    await self.page.inner_text(action.selector)
                )
            }
        elif isinstance(action, ElementXpath):
            return {
                'Image': await Render.render(
                    await get_elements_all(self.page, action.selector)
                )
            }
        elif isinstance(action, ElementDownload):
            async with self.page.expect_download() as download_info:
                await self.page.click(action.selector)
            download = await download_info.value
            return {'file': (open(await download.path(), 'rb'), download.suggested_filename),'Plain': '上传中...'}
        elif isinstance(action, ElementPdf):
            return {
                'file': (
                    await self.page.pdf(
                        width = action.width or "8.27in", 
                        height = action.height or "11.7in", 
                        print_background = True
                    ),
                    f'{self.page.url}.pdf'
                ),
                'Plain': '上传中...'
            }
        else:
            raise Exception('Unknown action')
        await asyncio.sleep(1)
        return {'Image': await self.page.screenshot()}

    async def handle_page(self, page):
        self.page = page
        await page.wait_for_load_state()

    def network(self):
        self.page.on("request", self.play_request)
        self.page.on("response", self.play_response)
        self.page.on("console", self.play_console)

    async def play_console(self, msg):
        values = []
        for arg in msg.args:
            values.append(str(await arg.json_value()))
        self.Network.console.append(''.join(values))

    def play_request(self, request) -> None:
        self.Network.request.append({'method': request.method, 'url': request.url, 'headers': request.headers})

    def play_response(self, response) -> None:
        self.Network.response.append({'status': response.status, 'url': response.url, 'headers': response.headers, 'body': response.body})

class MyList(list):

    def get(self, index):
        index = int(index)
        if 0 <= index < len(self):
            return self[index]
        else:
            None

class strtoAction:
    '''命令转Action'''
    
    @staticmethod
    def get_action(s: str) -> Action:
        s = s.split()
        if s[0] == 'goto':
            s = MyList(strtoAction.get_commend(s, '-u', '-t'))
            return ActionGoto(s[1], int(s.get(2) or 0))
        elif s[0] == 'click':
            s = MyList(strtoAction.get_commend(s, '-s', '-t'))
            return ActionClick(s[1], int(s.get(2) or 0))
        elif s[0] == 'fill':
            s = MyList(strtoAction.get_commend(s, '-s', '-w'))
            return ActionFill(s[1], s[2])
        elif s[0] == 'press':
            s = MyList(strtoAction.get_commend(s, '-s', '-k', '-t'))
            return ActionPress(s[1], s[2], int(s.get(3) or 0))
        elif s[0] == 'evaluate':
            s = MyList(strtoAction.get_commend(s, '-m', '-t'))
            return ActionEvaluate(s[1], int(s.get(2) or 0))
        elif s[0] == 'mouse':
            s = MyList(strtoAction.get_commend(s, '-y', '-x', '-t'))
            return ActionMouse(int(s.get(2) or 0), int(s.get(1) or 0), int(s.get(3) or 0))
        elif s[0] in ('screenshot', 'sc'):
            s = MyList(strtoAction.get_commend(s, '-p'))
            return ActionScreenshot(s.get(1))
        elif s[0] in ('fsc', 'full-screenshot'):
            s = MyList(strtoAction.get_commend(s, '-p'))
            return ActionScreenshot(s.get(1), True)
        elif s[0] in ('locatorscreenshot', 'lsc'):
            s = MyList(strtoAction.get_commend(s, '-s', '-p'))
            return ActionLocatorScreenshot(s[1], s.get(2))
        elif s[0] in ('resqest', 'req'):
            s = MyList(strtoAction.get_commend(s, '-n'))
            return ElementRequest(int(s[1]))
        elif s[0] in ('response', 'rep'):
            s = MyList(strtoAction.get_commend(s, '-n'))
            return ElementResponse(int(s[1]))
        elif s[0] in ('console', 'con'):
            s = MyList(strtoAction.get_commend(s, '-n'))
            return ElementConsole(int(s[1]))
        elif s[0] == 'html':
            s = MyList(strtoAction.get_commend(s, '-s'))
            return ElementHtml(s[1])
        elif s[0] == 'text':
            s = MyList(strtoAction.get_commend(s, '-s'))
            return ElementText(s[1])
        elif s[0] == 'xpath':
            s = MyList(strtoAction.get_commend(s, '-s'))
            return ElementXpath(s[1])
        elif s[0] == 'download':
            s = MyList(strtoAction.get_commend(s, '-s'))
            return ElementDownload(s[1])
        elif s[0] == 'pdf':
            s = MyList(strtoAction.get_commend(s, '-h', '-w'))
            return ElementPdf(s.get(1), s.get(2))
        else:
            raise Exception('Unknown action')

    def get_commend(s, *args):
        r = ''
        yield s[0]
        for i in range(1, len(s)):
            if s[i] in args:
                if r:
                    yield r
                    r = ''
            else:
                if r:
                    r += ' '
                r += s[i]
        if r:
            yield r
