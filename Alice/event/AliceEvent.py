from SimilarNeuron import (
    AsyncAdapterEvent, 
    EventName, 
    Result, 
    AsyncFramePenetration
    )
# from graia.ariadne.message.element import At
from ..internaltype import (
    MessageChain,
    UploadMethod,
    Plain,
    File,
    At,
    MusicShare,
    Image,
    FriendMessage,
    GroupMessage,
    Member,
    Group,
    Friend,
    GraiaMiraiApplication,
    Source,
    config
)
from ..utils import Thread
from ..scope import (
    MiraiBot,
    AliceBuiltins,
    Context, 
    AliceRelationship, 
    AliceSession,
    AliceSendMessage,
    AliceEventChain,
    Permissions,

    )
from ..parse import AliceParse, ParseRusult, ElementMatch, ParseMatch, ArgumentMatch, time_completion
from ..api import (
    qingyunke_chat,
    oneYan, 
    getBaike, 
    translation,
    AlphaZero, 
    getwiki,
    getBlog, 
    getMusic,
    cloudmusic,
    getImage_seovx,
    PlayExec, 
    Render,
    baidu_ORC,
    strtoAction,
    ParamikoClient,
    GithubParse,
    runCode,
    Language,
    ftp,
    ftp_file
)
import asyncssh, asyncio, inspect, os
from datetime import datetime
from functools import lru_cache
from playwright.async_api import Playwright, async_playwright

# 解析器映射
class ParseMapper:

    def __init__(self, parse: AliceParse, event: "AliceEvent"):
        self.event = event
        self.parse = parse

class Alice:

    @classmethod
    def parsemapper(cls):
        for i in cls.EventList():
            if hasattr(i, '__ParseMapper__'):
                yield ParseMapper(i.__ParseMapper__, i)

    @classmethod
    def get_subclasses(cls):
        for i in cls.__subclasses__():
            yield i
            yield from i.get_subclasses()
    
    @staticmethod
    @lru_cache(maxsize=100)
    def getevent_of_classname(name: str):
        for i in Alice.EventList():
            if i.__name__ == name:
                return i
        return None
    
    @staticmethod
    @lru_cache(maxsize=100)
    def getevent_of_evnetname(name: str):
        for i in Alice.EventList():
            if i.__eventname__ == name:
                return i
        return None

    @classmethod
    def EventList(cls):
        return [i for i in cls.get_subclasses() if hasattr(i, '__ParseMapper__')]
    
class AliceEvent(Alice):

    async def coupler(
        self, 
        group: Group,
        member: Member,
        friend: Friend,
        name: EventName,
        ):
        return (
            Context(
                bot = config['BotSession']['account'], 
                group = str(group.id) if group else None, 
                user = str(member.id if member else friend.id), 
                event = name
            ),
        )

    async def match(self, relation: AliceRelationship, context: Context) -> bool:
        res = relation.rematch(context, asyn=True)
        if await self.callfunc(res):
            return True
        return False

    async def callback(
        self, 
        friend: Friend, 
        group: Group, 
        result: Result, 
        apps: GraiaMiraiApplication, 
        source: Source,
        context: Context
        ):
        async with AsyncFramePenetration(MessageChain.create([Plain(result.first())])) as frame:
            await frame(AliceSendMessage.send)

class HelpEvent(AliceEvent, AsyncAdapterEvent):

    __ParseMapper__ = AliceParse(command=[ParseMatch('Help{event:>}')])

    __eventname__ = '帮助'

    __help__ = '''Help:
    command: `Help <查询内容>`
    description: 查看帮助'''

    async def funcevents(self):
        async def help(
            message: ParseRusult,
            relation: AliceRelationship,
            context: Context
            ):
            context.event = None
            loction = relation.location(context)
            for i in loction:
                if message.event in [i.__eventname__ for i in map(Alice.getevent_of_classname, i.event.iter)]:
                    return Alice.getevent_of_evnetname(message.event).__help__
            return f'未查询到 "{message.event}" 帮助!'
        return [help]       

class CommandEvent(AliceEvent, AsyncAdapterEvent):

    __ParseMapper__ = AliceParse(command=[ParseMatch('Command')])

    __eventname__ = '指令'

    __help__ = '''Command:
    command: `Command`
    description: 查看指令'''

    async def funcevents(self):
        async def command(
            message: ParseRusult,
            relation: AliceRelationship,
            context: Context
            ):
            context.event = None
            loction = relation.location(context)
            for i in loction:
                return '\n'.join([i.__eventname__ for i in map(Alice.getevent_of_classname, i.event.iter)])
            return f'未查询到 "{message.event}" 帮助!'
        return [command]

class TestEvent(AliceEvent, AsyncAdapterEvent):

    __ParseMapper__ = AliceParse(command=['测试'])

    __eventname__ = '测试'

    __help__ = '''
    command: 测试
    description: 无线终端中断测试
    '''

    async def funcevents(self):
        async def test(
            context: Context,
            EventChain: AliceEventChain
            ):
            async with AliceSession(AliceParse([r'([\s\S]*)', ElementMatch(At)]), context, EventChain, 600) as session:
                await session.send(MessageChain.create([Plain('收到😜')]))
                while True:
                    call = await session.wait()
                    if call:
                        await session.send(MessageChain.create([Plain(f'收到 {call.parserults.re}')]))
                    else:
                        break
        return [test]

    async def callback(self):
        ...

class oneYanEvent(AliceEvent, AsyncAdapterEvent):

    __ParseMapper__ = AliceParse(command=['一言'])

    __eventname__ = '一言'

    __help__ = '''Help:
    command: `一言`
    description: 返回一句随机的一言'''

    async def funcevents(self):
        return [oneYan]

class TranslationEvent(AliceEvent, AsyncAdapterEvent):

    __ParseMapper__ = AliceParse(
        command = ['翻译'],
        least = [([ParseMatch('翻译{text:>}'), ParseMatch('{text:<}翻译')], 1)]
    )

    __eventname__ = '翻译'

    __help__ = '''Help:
    command: `翻译 <文本>`
    description: 翻译文本'''

    async def funcevents(self, message: ParseRusult):
        async def asend():
            return await translation(message.text)
        return [asend]

class BaikeEvent(AliceEvent, AsyncAdapterEvent):

    __ParseMapper__ = AliceParse(
        command = ['百科'],
        least = [([ParseMatch('百科{text:>}'), ParseMatch('{text:<}百科')], 1)],
    )

    __eventname__ = '百科'

    __help__ = '''Help:
    command: `百科 <查询内容>`
    description: 返回查询内容的百科结果'''

    async def funcevents(self, message: ParseRusult):
        async def baike():
            return await Thread(target = getBaike, args = (message.text,)).start()
        return [baike]

class WikiEvent(AliceEvent, AsyncAdapterEvent):

    __ParseMapper__ = AliceParse(
        command = ['维基'],
        least = [([ParseMatch('维基{text:>}'), ParseMatch('{text:<}维基')], 1)],
    )

    __eventname__ = '维基'

    __help__ = '''Help:
    command: `维基 <查询内容>`
    description: 返回查询内容的维基结果'''

    async def funcevents(self, message: ParseRusult):
        async def baike():
            return await Thread(target = getwiki, args = (message.text,)).start()
        return [baike]

class BlogEvent(AliceEvent, AsyncAdapterEvent):

    __ParseMapper__ = AliceParse(
        command = ['博客'],
        least = [([ParseMatch('博客{text:>}'), ParseMatch('{text:<}博客')], 1)]
    )

    __eventname__ = '博客'

    __help__ = '''Help:
    command: `博客 <查询内容>`
    description: 返回查询内容的博客结果'''

    async def funcevents(self, message: ParseRusult):
        async def blog():
            return await Thread(target = getBlog, args = (message.text,)).start()
        return [blog]

class MusicEvent(AliceEvent, AsyncAdapterEvent):

    __ParseMapper__ = AliceParse(
        command = ['云音乐'],
        least = [([ParseMatch('云音乐{text:>}'), ParseMatch('{text:<}云音乐')], 1)],
    )

    __eventname__ = '云音乐'

    __help__ = '''Help:
    command: `云音乐 <查询内容>`
    description: 返回查询内容的音乐结果'''

    async def funcevents(
        self, 
        message: ParseRusult,
        EventChain: AliceEventChain,
        context: Context,
        app: GraiaMiraiApplication,
        source: Source
        ):
        async def music():
            try:
                d, lyric = await cloudmusic(message.text)
                await AliceSendMessage.send(
                    context, 
                    MessageChain.create([MusicShare(
                        kind= 'NeteaseCloudMusic', 
                        **d
                        )]), 
                    app)
                res = await Render.render(lyric)
                await AliceSendMessage.send(
                    context,
                    MessageChain.create([Image(data_bytes=res)]),
                    app)
            except:
                await AliceSendMessage.send(
                    context, 
                    MessageChain.create([Plain('查询失败')]), 
                    app,
                    source
                    )
        return [music]

    async def callback(self):
        ...

class ImageEvent(AliceEvent, AsyncAdapterEvent):

    __ParseMapper__ = AliceParse(command=['美图'])

    __eventname__ = '美图'

    __help__ = '''Help:
    command: `美图`
    description: 返回查询内容的图片'''

    async def funcevents(self):
        return [getImage_seovx]
    
    async def callback(
        self, 
        friend: Friend, 
        group: Group, 
        result: Result, 
        apps: GraiaMiraiApplication, 
        context: Context,
        source: Source
        ):
        async with AsyncFramePenetration(MessageChain.create(Image(data_bytes = result.first()))) as frame:
            await frame(AliceSendMessage.send)

class SSHEvent(AliceEvent, AsyncAdapterEvent):

    __ParseMapper__ = AliceParse(command=['SSH'])

    __eventname__ = 'SSH'

    __help__ = '''Help:
    command: `SSH`
    description: 连接本地SSH服务器'''

    async def funcevents(self):
        async def assh(
            EventChain: AliceEventChain,
            context: Context
            ):
            sshtext = []
            async with AliceSession(AliceParse([r'([\s\S]*)']), context, EventChain, 600) as session:
                async def onssh(process):
                    '''监听SSH流'''
                    while True:
                        sshtext.append(await process.stdout.readline())

                async def sendssh():
                    '''发送SSH流'''
                    n = 0
                    while True:
                        n1 = len(sshtext)
                        if n1>n:
                            await session.send(MessageChain.create([Plain(''.join(sshtext[n:n1]))]))
                            n = n1
                        await asyncio.sleep(1)
                await session.send(MessageChain.create([Plain('正在连接...')]))
                async with asyncssh.connect(**config['SSH']) as conn:
                    async with conn.create_process(stderr=asyncssh.STDOUT) as process:
                        session.on(sendssh)
                        session.on(onssh, process)
                        await session.send(MessageChain.create([Plain('SSH 已连接, 发送exit断开会话!')]))
                        while True:
                            call = await session.wait()
                            if call:
                                for i in call.parserults.re.split('\n'):
                                    process.stdin.write(i + '\n')
                            else:
                                break
        return [assh]

    async def callback(self):
        ...

class ParamikoEvent(AliceEvent, AsyncAdapterEvent):

    __ParseMapper__ = AliceParse(command=['Paramiko'])

    __eventname__ = 'Paramiko'

    __help__ = '''Help:
    command: `Paramiko`
    description: 连接本地SSH服务器(交互式)'''

    async def funcevents(self):
        async def assh(
            EventChain: AliceEventChain,
            context: Context
            ):
            async with AliceSession(AliceParse([r'([\s\S]*)']), context, EventChain, 600) as session:
                async def sendssh(self):
                    n = 0
                    while True:
                        n1 = len(self.queue)
                        if n1 > n:
                            res = ''.join(self.queue[n:n1])
                            n = n1
                            await session.send(MessageChain.create([Plain(res)]))
                        else:
                            await asyncio.sleep(1)
                await session.send(MessageChain.create([Plain('正在连接...')]))
                async with ParamikoClient(**config['SSH']) as ssh:
                    session.on(sendssh, ssh)
                    while True:
                        call = await session.wait()
                        if call:
                            await ssh.cmd(call.parserults.re)
                        else:
                            break
        return [assh]
    
    async def callback(self):
        ...

class AlphaZeroEvent(AliceEvent, AsyncAdapterEvent):

    __ParseMapper__ = AliceParse(command=['AlphaZero'])

    __eventname__ = 'AlphaZero'

    __help__ = '''Help:
    command: `AlphaZero`
    description: 开始AlphaZero游戏'''

    async def funcevents(self):
        async def alphazero(
            EventChain: AliceEventChain,
            context: Context
            ):
            Al = AlphaZero()
            async with AliceSession(AliceParse([r'([\s\S]*)']), context, EventChain, 600) as session:
                await session.send(MessageChain.create([Plain(f"AlphaZero 已开始, 发送 `exit` 退出\n\n玩家默认执黑棋`●`\n\n{Al.get_str()}")]))
                while True:
                    call = await session.wait()
                    back = Al.ai(*[int(n) for n in call.parserults.re.split()][::-1])
                    if back:
                        await session.send(MessageChain.create([Plain(back)]))
                    else:
                        await session.send(MessageChain.create([Plain('AlphaZero 落子错误')]))
        return [alphazero]

    async def callback(self):
        ...

class PlaywrightEvent(AliceEvent, AsyncAdapterEvent):

    __ParseMapper__ = AliceParse(command=['Playwright'])

    __eventname__ = 'Playwright'

    __help__ = '''Help:
    command: `Playwright`
    description: 开始Playwright控制
    跳转: goto -u <网址> -t <超时>
    点击: click -s <元素选择器> -t <超时>
    输入: fill -s <元素选择器> -w <值>
    键盘: press -s <元素选择器> -k <键值> -t <超时>
    滚轮: move -y <Y轴> -x <X轴> -t <超时>
    js注入: evaluate -m <js代码> -t <超时>
    截图: [screenshot | sc] -p <保存路径>
    全截图: [fullscreenshot | fsc] -p <保存路径>
    元素截图: [locatorscreenshot | lsc] -s <元素选择器> -p <保存路径>
    请求: [resqest | req] -n <返回数量>
    响应: [response | rep] -n <返回数量>
    控制台: [console | con] -n <返回数量>
    元素源代码: html -s <元素选择器>
    元素文本: text -s <元素选择器>
    元素xpath: xpath -s <元素选择器>
    下载: download -s <元素选择器>
    pdf: pdf -h <页面高> -w <页面宽>   
    '''

    async def funcevents(
        self,
        context: Context,
        EventChain: AliceEventChain
        ):
        async def asend():
            async with async_playwright() as playwright, PlayExec(playwright) as Play:
                async with AliceSession(AliceParse([r'([\s\S]*)']), context, EventChain, 600) as session:
                    await session.send(MessageChain.create([Plain('Playwright 已启动!')]))
                    while True:
                        call = await session.wait()
                        if call:
                            try:
                                res = await Play.play(strtoAction.get_action(call.parserults.re))
                                await session.sendofdict(res)
                            except Exception as e:
                                await session.send(MessageChain.create([Plain(str(e))]))
                        else:
                            break
        return [asend]

    async def callback(self):
        ...

class AliceStatusWindow(AliceEvent, AsyncAdapterEvent):
    
    __ParseMapper__ = AliceParse(command=['史提西亚之窗'])

    __eventname__ = '史提西亚之窗'

    __help__ = '''Help:
    command: `史提西亚之窗 -> [system call] <command>`
    description: 开启史提西亚之窗'''

    async def funcevents(
        self,
        builtins: AliceBuiltins,
        context: Context,
        EventChain: AliceEventChain,
    ):
        builtins.update(globals())
        async def asend():
            async with AliceSession(AliceParse([r'([\s\S]*)']), context, EventChain, 600) as session:
                await session.send(MessageChain.create([Plain('"史提西亚之窗" 已开启!')]))
                while True:
                    call = await session.wait()
                    if call:
                        text = call.parserults.re.split('\n')
                        if text[0] == 'system call':
                            res = await Thread(target=exec, args=('\n'.join(text[1:]), builtins)).start()
                        else:
                            res = await Thread(target = eval, args = (call.parserults.re, builtins)).start()
                        res = await Render.render(str(res))
                        await session.send(MessageChain.create([Image(data_bytes = res)]))
                    else:
                        break
        return [asend]

    async def callback(self):
        ...

class BaiduOrcEvent(AliceEvent, AsyncAdapterEvent):
    
    __ParseMapper__ = AliceParse(command=['识别', ElementMatch(Image)])
    
    __eventname__ = '识别'

    __help__ = '''Help:
    command: `识别`
    description: 识别图片'''
    
    async def funcevents(
        self,
        message: ParseRusult
    ):
        async def asend():
            return await baidu_ORC(message.ele)
        return [asend]

class GithubEvent(AliceEvent, AsyncAdapterEvent):

    __ParseMapper__ = AliceParse(command = [ParseMatch('github {text}')])

    __eventname__ = 'github'

    __help__ = '''Help:
    command: `github [user | repo | org] [-f | -h] {command}`
    description: Github操作'''

    async def funcevents(
        self,
        message: ParseRusult,
        context: Context,
        EventChain: AliceEventChain,
    ):
        async def asend():
            async with AliceSession(AliceParse([r'([\s\S]*)']), context, EventChain, 600) as session:
                await session.sendofdict(await Thread(target = GithubParse.parse_action, args = (message.text,)).start())
        return [asend]
    
    async def callback(self):
        ...

class PermissionsEvent(AliceEvent, AsyncAdapterEvent):

    __ParseMapper__ = AliceParse(command = [ParseMatch('Pm {text}')])

    __eventname__ = '权限'

    __help__ = '''Help:
    command: `Pm [-r | -c | -d] | [bot | group | user | event] {command}`
    description: 查看权限'''

    async def funcevents(self, message: ParseRusult):
        async def permiss():
            return await Thread(target = Permissions.action, args = (message.text,)).start()
        return [permiss]

class RemindEvent(AliceEvent, AsyncAdapterEvent):

    __ParseMapper__ = AliceParse(command = [ParseMatch('提醒 {text}')])

    __eventname__ = '提醒'

    __help__ = '''Help:
    command: `提醒 [-w | -d] [%Y-%m-%d %H:%M:%S] {提醒内容}`
    description: 提醒'''

    async def funcevents(
        self, 
        message: ParseRusult,
        context: Context,
        EventChain: AliceEventChain,
        ):

        async def remind():
            def timing(date):
                res = datetime(*date) - datetime.now()
                if res.days < 0:
                    return '提醒时间已过期!'
                return res
            text = message.text.split()
            async with AliceSession(AliceParse([r'([\s\S]*)']), context, EventChain, 600) as session:
                if len(text) < 3:
                    await session.send(MessageChain.create([Plain('提醒格式错误')]))
                    return False
                elif text[0] == '-d':
                    res = time_completion(' '.join(text[1:]))
                    if isinstance(res, str):
                        await session.send(MessageChain.create([Plain(res)]))
                        return res
                    res = timing(res)
                    if isinstance(res, str):
                        await session.send(MessageChain.create([Plain(res)]))
                        return res
                    await session.send(MessageChain.create([Plain('还有{}天{}小时{}分钟{}秒 提醒!'.format(res.days, res.seconds//3600, res.seconds%3600//60, res.seconds%60))]))
                    await asyncio.sleep(res.seconds + res.days * 24 * 3600)
                    await session.send(MessageChain.create([Plain(text[-1])]))
                elif text[0] == '-w':
                    if len(text[1:-1]) == 1:
                        res = text[1].split(':')
                        if len(res) == 3:
                            date = datetime.strptime(text[1], '%H:%M:%S')
                            await session.send(MessageChain.create([Plain('还有{}小时{}分钟{}秒 提醒!'.format(date.hour, date.minute, date.second))]))
                        elif len(res) == 2:
                            date = datetime.strptime(text[1], '%M:%S')
                            await session.send(MessageChain.create([Plain('还有{}分钟{}秒 提醒!'.format(date.minute, date.second))]))
                        elif len(res) == 1:
                            date = datetime.strptime(text[1], '%S')
                            await session.send(MessageChain.create([Plain('还有{}秒 提醒!'.format(date.second))]))
                        else:
                            await session.send(MessageChain.create([Plain('提醒格式错误')]))
                            return False
                        await asyncio.sleep(res.seconds + res.days * 24 * 3600)
                        await session.send(MessageChain.create([Plain(text[-1])]))                    
        return [remind]
        
    async def callback(self):
        ...

class RunCodeEvent(AliceEvent, AsyncAdapterEvent):
    
    __ParseMapper__ = AliceParse(command = ['runCode'])

    __eventname__ = 'runCode'

    __help__ = f'''Help:
    command: `runCode -> code -> language -> stdin`
    description: 运行代码
    language: {' '.join(Language.keys())}
    '''

    async def funcevents(
        self,
        context: Context,
        EventChain: AliceEventChain,
        ):
    
        async def run():
            async with AliceSession(AliceParse([r'([\s\S]*)']), context, EventChain, 600) as session:
                await session.send(MessageChain.create([Plain('请输入要运行的code...')]))
                call = await session.wait()
                code = call.parserults.re
                await session.send(MessageChain.create([Plain('请输入要运行的语言...')]))
                while True:
                    call = await session.wait()
                    if call.parserults.re in Language.keys():
                        language = call.parserults.re
                        break
                    else:
                        await session.send(MessageChain.create([Plain('语言不存在，请重新输入...')]))
                await session.send(MessageChain.create([Plain('是否有运行code的输入(Y,N)...')]))
                call = await session.wait()
                if call.parserults.re in ('是', 'Y', 'y', 'yes', 'Yes'):
                    await session.send(MessageChain.create([Plain('请输入要运行code的输入(多个输入以换行分隔)...')]))
                    call = await session.wait()
                    stdin = call.parserults.re
                    res = await Thread(target = runCode, args = (code, language, stdin)).start()
                    await session.send(MessageChain.create([Plain(res)]))
                elif call.parserults.re in ('否', 'N', 'n', 'no', 'NO'):
                    res = await Thread(target = runCode, args = (code, language)).start()
                    await session.send(MessageChain.create([Plain(res)]))
        return [run]

    async def callback(self):
        ...

class FtpEvent(AliceEvent, AsyncAdapterEvent):
        
        __ParseMapper__ = AliceParse(command = [ParseMatch('ftp{path:>}')])
    
        __eventname__ = 'ftp'
    
        __help__ = '''Help:
        command: `ftp [-d | -u] {path}`
        description: ftp
        '''
    
        async def funcevents(
            self,
            message: ParseRusult,
            app: GraiaMiraiApplication,
            context: Context,
            EventChain: AliceEventChain,
            ):
        
            async def sendftp():
                async with AliceSession(AliceParse([r'([\s\S]*)']), context, EventChain, 600) as session:
                    path = message.path.split()
                    if len(path) == 2:
                        if path[0] == '-d':
                            res = await ftp(path[1])
                            if isinstance(res, str):
                                await session.send(MessageChain.create([Plain(res)]))
                            else:
                                res.update({'Plain': '上传中...'})
                                await session.sendofdict(res)
                        elif path[0] == '-u':
                            await session.send(MessageChain.create([Plain('请输上传文件')]))
                            call = await session.wait(AliceParse([ElementMatch(File)]))
                            file = await app.getFileInfo(session.GrouporFriend, call.parserults.ele[0].id, True)
                            await ftp_file(path[1], file.name, file.download_info.url)
                            await session.send(MessageChain.create([Plain(f'文件已上传至 {os.path.join(path[1], file.name)}')]), False)
                    else:
                        await session.send(MessageChain.create([Plain('ftp命令错误...')]))
            return [sendftp]
    
        async def callback(self):
            ...                            

class RetractEvent(AliceEvent, AsyncAdapterEvent):
        
        __ParseMapper__ = AliceParse(command = [ParseMatch('撤回{num:>}')])
    
        __eventname__ = '撤回'
    
        __help__ = '''Help:
        command: `撤回 {num}`
        description: 撤回消息
        '''
    
        async def funcevents(
            self,
            context: Context,
            app: GraiaMiraiApplication,
            message: ParseRusult,
            ):
        
            async def retract():
                e = int(message.num)
                n = 0
                if context.group:
                    for i in AliceSendMessage.sendid[::-1]:
                        if n >= e:
                            break
                        if i[0] == context.group:
                            await app.recallMessage(i[1])
                            AliceSendMessage.sendid.put(i)
                            n += 1
                    print(list(AliceSendMessage.sendid))
            return [retract]
    
        async def callback(self):
            ...

class ChatEvent(AliceEvent, AsyncAdapterEvent):
    
    __ParseMapper__ = AliceParse(command = [r'([\s\S]*)', ArgumentMatch({'target': int(config['BotSession']['account'])}, At)])

    __eventname__ = '聊天'

    __help__ = '''Help:
    command: `At {text}`
    description: 聊天'''

    async def funcevents(
        self, 
        message: ParseRusult
        ):
        async def chat():
            return await qingyunke_chat(message.re)
        return [chat]
