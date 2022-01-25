from SimilarNeuron import (
    AsyncAdapterEvent, 
    EventName, 
    Result, 
    AsyncFramePenetration
    )

from ..internaltype import (
    MessageChain,
    UploadMethod,
    Plain,
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

from ..scope import (
    MiraiBot,
    AliceBuiltins,
    Context, 
    AliceRelationship, 
    AliceSession,
    AliceSendMessage,
    AliceEventChain,
    Permissions
    )

class PassiveEvent:

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

    async def callback(
        self, 
        friend: Friend, 
        group: Group, 
        result: Result, 
        apps: GraiaMiraiApplication, 
        source: Source,
        context: Context
        ):
        async with AsyncFramePenetration(MessageChain.create(Plain(result.first()))) as frame:
            await frame(AliceSendMessage.send)

class GroupRecallEvent:
    ...
