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
    At,
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
from .. scope import AliceSendMessage, Context
from ..parse import Timing 


class TimingEvent:
    
    @classmethod
    async def send(cls, message: MessageChain, app: GraiaMiraiApplication):
        await AliceSendMessage.send(cls.context, message, app)

    @classmethod
    def subclasses(cls):
        for i in cls.__subclasses__():
            if hasattr(i, '__eventname__'):
                yield i
    
