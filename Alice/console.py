from .common import Common, GraiaApp, Monitor, AliceSession
from .api import Render
from .internaltype import config
from .model import ModelCore
import asyncio


async def event_distributor(loop: "asyncio.AbstractEventLoop", queue: "asyncio.Queue"):
    '''事件分发器'''
    while True:
        event = await queue.get()
        loop.create_task(Monitor.on_message(event))
        loop.create_task(AliceSession.on_session(event))

class Console(Common):
    def __init__(self, app: GraiaApp = config['Alice']):
        super().__init__(app)
        Common.loop.create_task(event_distributor(Common.loop, Common.eventqueue))
        Common.loop.create_task(Render.start()) # 启动文本渲染器
        if app == GraiaApp.Application:
            Common.app.launch_blocking()
        elif app == GraiaApp.Ariadne:
            Common.loop.run_until_complete(Common.app.lifecycle())
