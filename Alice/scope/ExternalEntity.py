from SimilarNeuron import Ordinary, AsyncRelation, BaseContext, BaseMapperEvent
from graia.ariadne.message.element import Source
from ..internaltype import (
    MessageChain,
    Plain,
    Group,
    Friend,
    GraiaMiraiApplication
)
from ..model import ModelCore
from typing import Optional, Union, Iterable, List, Any

# 定义外部实体作用域
class MiraiBot(Ordinary):
    ModelCore.init_graia(True) # 初始化模型

    def __init__(self, name: str, subiter: Iterable):
        subiter = ModelCore.create_alice(self.__class__.__name__, name, subiter) # 双向绑定
        setattr(MiraiBot, self.__class__.__name__, self)
        super().__init__(name, subiter, reference = True)

    def add(self, *identification: Iterable[Any]) -> None:
        ModelCore.create_alice(
            self.__class__.__name__, self.name, list(identification)
        )

        return super().add(*identification)

    def remove(self, *identification: Iterable[Any]) -> None:
        ModelCore.remove_graia(self.__class__.__name__, self.name, identification)
        return super().remove(*identification)

class GraiaBot(MiraiBot):
    ...

class GraiaGroup(MiraiBot):
    ...

class GraiaUser(MiraiBot):
    ...

class GraiaEvent(MiraiBot):
    ...

# Monitor 元类
class BaseMonitor(type):
    ...

# 定义权鉴依赖类型
class Context(BaseContext):
    name: str = 'Context'
    bot: Optional[Union[GraiaBot, str]] = None
    group: Optional[Union[GraiaGroup, str]] = None
    user: Optional[Union[GraiaUser, str]] = None
    event: Optional[Union[GraiaEvent, str]] = None

# 定义冷却延迟
class AliceRelation(AsyncRelation):

    async def cooling(
        self,
        frined: Friend, 
        group: Group, 
        apps: GraiaMiraiApplication, 
        source: Source
        ):
        if frined:
            await apps.sendFriendMessage(frined, MessageChain.create([Plain('冷却中')]), quote = source)
        elif group:
            await apps.sendGroupMessage(group, MessageChain.create([Plain('冷却中')]), quote = source)

# Alice 内建对象
class AliceBuiltins(dict):
    ...

class AliceRelationship(BaseMapperEvent):
    
    def __init__(self, name: str, region: Ordinary, contact: List[BaseContext]):
        res = [
            Context(
                name=i['name'],
                bot=getattr(GraiaBot, i['bot']),
                group=getattr(GraiaGroup, i['group']) if i['group'] else None,
                user=getattr(GraiaUser, i['user']),
                event=getattr(GraiaEvent, i['event']),
                direction=i['direction'],
                relationship=AliceRelation(
                    frequency=(i['relationship'][0][0], i['relationship'][0][1]),
                    delayed=i['relationship'][1],
                ),
            )
            for i in ModelCore.create_relation(name, contact)
        ]

        super().__init__(name, region, res)
        setattr(AliceRelationship, name, self)
        [setattr(self, i.name, i) for i in res]

    def structure(self):
        return {
            i.name: {k: list(v) for k, v in i.filterNone.items()}
            for i in self.iter
        }
