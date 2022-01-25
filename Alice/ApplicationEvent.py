from .internaltype import (
    FriendMessage,
    GroupMessage,
    FriendRecallEvent,
    GroupRecallEvent,
    Member,
    Group,
    Friend,
    MessageChain,
    GraiaMiraiApplication,
    Source,
)
from .common import Common
from .scope import AliceEventChain

class ApplicationEvent:

    @Common.bcc.receiver(FriendMessage)
    async def on_friend_message(app: GraiaMiraiApplication, friend: Friend, message: MessageChain, source: Source):
        await Common.eventqueue.put(AliceEventChain(FriendMessage, locals()))

    @Common.bcc.receiver(GroupMessage)
    async def on_group_message(app: GraiaMiraiApplication, group: Group, message: MessageChain, sender: Member, source: Source):
        await Common.eventqueue.put(AliceEventChain(GroupMessage, locals()))

    @Common.bcc.receiver(GroupRecallEvent)
    async def on_group_recall(app: GraiaMiraiApplication, group: Group, sender: Member, recal: GroupRecallEvent):
        await Common.eventqueue.put(AliceEventChain(GroupRecallEvent, locals()))

    @Common.bcc.receiver(FriendRecallEvent)
    async def on_friend_recall(app: GraiaMiraiApplication, friend: Friend, recal: FriendRecallEvent):
        await Common.eventqueue.put(AliceEventChain(FriendRecallEvent, locals()))
