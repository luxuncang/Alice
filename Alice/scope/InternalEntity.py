from SimilarNeuron import Ordinary, TimeList, TimeBoundCache
from graia.ariadne.message.element import Source
from ..internaltype import (
    MessageChain,
    Plain,
    Image,
    At,
    AtAll,
    FlashImage,
    Voice,
    Face,
    FriendMessage,
    GroupMessage,
    Member,
    Group,
    Friend,
    GraiaMiraiApplication
)
from ..parse import AliceParse, ParseRusult
from .ExternalEntity import Context, GraiaBot, GraiaGroup, GraiaUser, GraiaEvent,MiraiBot
from ..agreement import DictToMessageChain
from ..exception import AliceSessionStop
from typing import Dict, Any, Callable, Union, Iterable, List, Optional, BinaryIO
import enum, asyncio

class GraiaApp(str, enum.Enum):
    """
    GraiaApp 类是一个枚举类，用于描述 Graia 应用的类型。
    """
    Application = 'Application'
    Ariadne = 'Ariadne'
    Avilla = 'Avilla'

# Alice消息链
class AliceEventChain:
    '''Graia事件载体
    '''

    def __init__(self, evnet, context: Dict[str, Any]):
        self.event = evnet
        self.context = context
        self.type = {type(i):i for i in context.values()}

    def gettype(self, mold: type):
        return self.type.get(mold)

# 回调会话
class CallbackSession:

    def __init__(self, context: Dict[str, Any], parserults: ParseRusult):
        self.context = context
        self.parserults = parserults
        self.type = {type(i):i for i in context.values()}

    def gettype(self, mold: type):
        return self.type.get(mold)

# 发送器
class AliceSendMessage:
    sendid = TimeList(timeout=120)

    @staticmethod
    async def send(context: Context, message: MessageChain, app: GraiaMiraiApplication, source: Source = None):
        if context.group:
            res = await app.sendGroupMessage(int(context.group), message, quote = source)
        else:
            res = await app.sendFriendMessage(int(context.user), message, quote = source)
        if context.group:
            AliceSendMessage.sendid.add((context.group, res.messageId))
        return res

# 新式会话
class AliceSession:
    session = TimeList(60)
    callbake = {}

    def __init__(
        self,
        parse: AliceParse,
        context: Context,
        EventChain: AliceEventChain,
        timeout: int = 60,
        loop: asyncio.AbstractEventLoop = None,
        exit: AliceParse = AliceParse(['exit'])) -> None:
        self.parse = parse
        self.context = context
        self.call = EventChain
        self.timeout = timeout
        if loop:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()
        self.app: GraiaMiraiApplication = self.call.gettype(GraiaMiraiApplication)
        self.ons = []
        self.exit = exit

    async def __aenter__(self) -> "AliceSession":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        AliceSession.session.put(self)

    async def match(self, context: AliceEventChain) -> bool:
        if self.ChaintoContext(context):
            eres = self.exit.match(context.gettype(MessageChain))
            if eres:
                return AliceSessionStop
            res = self.parse.match(context.gettype(MessageChain))
            if res:
                return res
        return False

    def ChaintoContext(self, context: AliceEventChain) -> bool:
        if context.event == FriendMessage and (not self.context.group):
            if self.context.user == str(context.gettype(Friend).id):
                return True
        elif context.event == GroupMessage and self.context.group:
            if (
                self.context.group == str(context.gettype(Group).id) and
                self.context.user == str(context.gettype(Member).id)
            ):
                return True
        return False

    @classmethod
    async def on_session(cls, messages: AliceEventChain) -> None:
        for s in cls.session:
            res = await s.match(messages)
            if res == AliceSessionStop:
                print('session stop')
                AliceSession.callbake[s] = AliceSessionStop
                cls.session.put(s)
                break

            if res:
                print('进入新式会话')
                AliceSession.callbake[s] = CallbackSession(messages.context, res)
                cls.session.put(s)
                break

    async def wait(self, parse: AliceParse = None, context: Context = None, timeout = None) -> CallbackSession:

        if parse:
            self.parse = parse

        if context:
            self.context = context

        if timeout:
            self.timeout = timeout

        AliceSession.session.add(self, self.timeout)

        while True:
            if AliceSession.callbake.get(self):
                self.call = AliceSession.callbake.pop(self)
                if self.call == AliceSessionStop:
                    await self.close()
                    break
                return self.call
            await asyncio.sleep(1)

    async def send(self, message: MessageChain, sourse: bool = True):
        return await AliceSendMessage.send(
            self.context,
            message,
            self.app,
            self.call.gettype(Source) if sourse else None
        )

    async def sendofdict(self, message: Dict[str, Union[str, bytes, BinaryIO]]):
        if 'file' in message:
            self.loop.create_task(
                self.app.uploadFile(
                    data = message['file'][0],
                    name = message['file'][1],
                    target = self.GrouporFriend
                )
            )
            del message['file']
        return await self.send(DictToMessageChain.transformation(message))

    def on(self, func: Callable, *args, **kwargs) -> None:
        self.ons.append(self.loop.create_task(func(*args, **kwargs)))

    async def close(self):
        await self.send(MessageChain.create([Plain('退出会话')]), False)
        for i in self.ons:
            i.cancel()
        return AliceSessionStop

    @property
    def GrouporFriend(self):
        if self.context.group:
            return self.call.gettype(Group)
        else:
            return self.call.gettype(Friend)

# 权限控制
class Permissions:
    
    @staticmethod
    def get_class(obj: str):
        if obj == 'bot':
            return GraiaBot
        elif obj == 'user':
            return GraiaUser
        elif obj == 'group':
            return GraiaGroup
        elif obj == 'event':
            return GraiaEvent
        return f"{obj} is not a valid object"

    @staticmethod
    def get_subclass(obj, name):
        if obj == 'bot':
            return getattr(GraiaBot, name, f'{name} 不在 GraiaBot 标签中')
        elif obj == 'user':
            return getattr(GraiaUser, name, f'{name} 不在 GraiaUser 标签中')
        elif obj == 'group':
            return getattr(GraiaGroup, name, f'{name} 不在 GraiaGroup 标签中')
        elif obj == 'event':
            return getattr(GraiaEvent, name, f'{name} 不在 GraiaEvent 标签中')
        return f"{obj} is not a valid object"

    @classmethod
    def read(cls, obj, name):
        if isinstance(obj, str):
            return obj
        ob = getattr(obj, name, None)
        if ob:
            return '\n'.join(list(ob))
        return f"{name} 不在 {obj} 中!"

    @classmethod
    def add(cls, obj, name):
        if isinstance(obj, str):
            return obj
        ob = getattr(obj, name, None)
        if ob:
            return f'{name} 在 {obj} 已经存在!'
        obj(name, [])
        return f'{name} 在 {obj} 增加成功!'
    
    @classmethod
    def remove(cls, obj, name):
        if isinstance(obj, str):
            return obj
        ob = getattr(obj, name, None)
        if ob:
            delattr(obj, name)
            return f'{name} 在 {obj} 删除成功!'
        return f'{name} 在 {obj} 不存在!'

    @classmethod
    def label_add(cls, obj, name):
        if isinstance(obj, str):
            return obj
        if name in list(obj):
            return f'{name} 在 {obj} 已经存在!'
        obj.add(name)
        return f'{name} 在 {obj} 增加成功!'
    
    @classmethod
    def label_remove(cls, obj, name):
        if isinstance(obj, str):
            return obj
        if name in list(obj):
            obj.remove(name)
            return f'{name} 在 {obj} 删除成功!'
        return f'{name} 在 {obj} 不存在!'

    @classmethod
    def action(cls, parse: str):
        parse = parse.split()
        if len(parse) == 1 and parse[0] in ('bot', 'user', 'group', 'event'):
            return '\n'.join([i.name for i in cls.get_class(parse[0])])
        elif all([len(parse) == 3, parse[0] in ('bot', 'user', 'group', 'event'), parse[1] in ('-c', '-d', '-r')]):
            if parse[1] == '-r':
                return cls.read(cls.get_class(parse[0]), parse[2])
            elif parse[1] == '-c':
                return cls.add(cls.get_class(parse[0]), parse[2])
            elif parse[1] == '-d':
                return cls.remove(cls.get_class(parse[0]), parse[2])
        elif all([len(parse) == 4, parse[0] in ('bot', 'user', 'group', 'event'), parse[2] in ('-c', '-d')]):
            if parse[2] == '-c':
                return cls.label_add(cls.get_subclass(parse[0], parse[1]), parse[3])
            elif parse[2] == '-d':
                return cls.label_remove(cls.get_subclass(parse[0], parse[1]), parse[3])
        return '指令解析错误!'
