import asyncio
import traceback
from typing import List

from Alice.event.AliceEvent import AliceEvent
from Alice.model.core import Group
from .utils import EventQueue
from .scope import (
    GraiaBot, 
    GraiaGroup, 
    GraiaUser, 
    GraiaEvent, 
    MiraiBot, 
    Context, 
    AliceRelation, 
    AliceRelationship, 
    AliceEventChain, 
    GraiaApp,
    AliceSession,
    AliceBuiltins
)
from .agreement import Agreement
from .event import (
    Alice,
    ParseMapper,
    AsyncAdapterEvent,
    TimingEvent
    )
from .parse import ParseRusult
from .internaltype import (
    config, 
    GroupMessage,
    FriendMessage,
    MessageChain, 
    Broadcast,
    GraiaMiraiApplication,
    Session
)


# 重要事件
VitalEvent = [
    'FtpEvent',
    'RetractEvent',
    'TestEvent',
    'SSHEvent', 
    'PermissionsEvent',
    'ParamikoEvent',
    'AliceStatusWindow',
]

# 限制事件
LimitedEvent = [
    'PlaywrightEvent',
    'RemindEvent'
]

# 普通事件
GeneralEvent = [
    'RunCodeEvent',
    'TranslationEvent',
    'oneYanEvent', 
    'WikiEvent',
    'BaikeEvent', 
    'AlphaZeroEvent', 
    'BlogEvent', 
    'MusicEvent', 
    'WeatherEvent', 
    'ImageEvent',
    'HelpEvent',
    'CommandEvent',
    'BaiduOrcEvent',
    'GithubEvent',
    'ChatEvent',
    ]

# 所有事件
AllEvent = GeneralEvent + VitalEvent + LimitedEvent

GraiaBot('Fluctlight', []) # (人工摇光)
GraiaGroup('UnderWorld', []) # Under World(地下世界)
GraiaGroup('ALfheimOnline', []) # ALfheim Online(精灵之国)
GraiaUser('System', []) # System(创世之神·史提西亚)
GraiaUser('Source', []) # Source(索鲁斯)
GraiaEvent(
    'StatusWindow',
    AllEvent
    ) # Status Window(史提西亚之窗)
GraiaEvent('Gigascedar', []) # Gigascedar(基加斯西达之树)

# 定义关系
AliceRelationship(
    'Alice',
    MiraiBot,
    [
        Context(
            name = '群组高级权限域',
            bot = GraiaBot.Fluctlight, 
            group = GraiaGroup.UnderWorld,
            user = GraiaUser.System,
            event = GraiaEvent.StatusWindow,
        ),
        Context(
            name = '会话高级权限域',
            bot = GraiaBot.Fluctlight,
            user = GraiaUser.System,
            event = GraiaEvent.StatusWindow,
        ),
        Context(
            name = '群组一般权限域',
            bot = GraiaBot.Fluctlight, 
            group = GraiaGroup.ALfheimOnline, 
            user = GraiaUser.Source,
            event = GraiaEvent.Gigascedar, 
            relationship = AliceRelation(frequency = (1, 60), delayed = 1),
            direction = False
        )
    ]
)


class Common(object):
    """
    Common class for all classes.
    """
    relation = AliceRelationship.Alice # 关系
    entoin = Agreement()               # 转换协议
    timingevent = {}
    builtins = AliceBuiltins(         
        {
            'relation': relation,
            'eventqueue': EventQueue,
            'config': config,
        }
    )                                  # Alice内建对象

    def __init__(self, console: GraiaApp):
        self.console = console
        Common.eventqueue = EventQueue()
        self.config = config
        self.run()

    def run(self):
        """
        Run the application.
        """
        if self.console == GraiaApp.Application:
            self.Application()
        elif self.console == GraiaApp.Ariadne:
            self.Ariadne()
        elif self.console == GraiaApp.Avilla:
            self.Avilla()
    
    def Avilla(self):
        """
        Avilla class.
        """
        pass

    def Ariadne(self):
        """
        Ariadne class.
        """
        Common.loop = asyncio.get_event_loop()
        Common.bcc = Broadcast(loop = Common.loop)
        Common.app = GraiaMiraiApplication(
            connect_info=Session(**self.config['BotSession']),
            loop=Common.loop,
            broadcast=Common.bcc,
            )
        Common.builtins.update({'app': Common.app, 'loop': Common.loop, 'bcc': Common.bcc})
        from .ApplicationEvent import ApplicationEvent

    def Application(self):
        """
        Application class.
        """
        Common.loop = asyncio.get_event_loop()
        Common.bcc = Broadcast(loop = Common.loop)
        Common.app = GraiaMiraiApplication(
            broadcast = Common.bcc,
            connect_info = Session(**self.config['BotSession'])
            )
        Common.builtins.update({'app': Common.app, 'loop': Common.loop, 'bcc': Common.bcc})
        from .ApplicationEvent import ApplicationEvent  # 引入事件

class Monitor:
    '''监听器'''

    session: AliceSession = AliceSession      # 会话列表
    parsemap: List[ParseMapper] = list(Alice.parsemapper())     # 匹配列表

    @classmethod
    def add_parsemap(cls, parsemapper: ParseMapper):
        """
        添加匹配规则。
        """
        cls.parsemap.append(parsemapper)

    @classmethod
    async def on_message(cls, messages: AliceEventChain):
        """
        消息监听器。
        """
        async def context(event: AsyncAdapterEvent, parse: ParseRusult):
            """
            内部函数，用于处理消息。
            """
            locals().update(messages.context)
            locals().update(
                {
                    'relation': Common.relation, 
                    'entoin': Common.entoin, 
                    'app': Common.app, 
                    'session': Monitor.session,
                    'loop': Common.loop,
                    'bcc': Common.bcc,
                    'builtins': Common.builtins,
                    'EventChain': messages,
                }
                )
            await event().run()

        if messages.event in (GroupMessage, FriendMessage):
            try:
                for i in cls.parsemap:
                    res = i.parse.match(messages.gettype(MessageChain))
                    if res:
                        await context(i.event, res)
                        break # 匹配成功，跳出循环
            except Exception:
                traceback.print_exc()
                traceback.format_exc()