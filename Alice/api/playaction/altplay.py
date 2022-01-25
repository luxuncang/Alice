import asyncio, os
from playwright.async_api import Playwright, async_playwright
from pprint import pprint
from .action import PlayExec, ActionGoto, ActionClick, ActionFill, ActionPress

async def playwright_run(playwright: Playwright) -> None:
    async with PlayExec(playwright) as paly:
        # 交互
        s = yield paly
        while True:
            s = yield await paly.play(s)

async def playmessage() -> None:
    async with async_playwright() as playwright:
        paly = playwright_run(playwright)
        runs = await paly.__anext__()
        s = yield runs
        while True:
           s =  yield await paly.asend(s)
