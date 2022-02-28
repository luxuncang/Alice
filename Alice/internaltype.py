import os, sys, yaml

onfile = os.path.split(sys.argv[0])[0]

with open(os.path.join(onfile, 'config.yaml'), encoding='utf-8') as f:
    data = f.read()
    config = yaml.safe_load(data)

from graia.broadcast import Broadcast
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne as GraiaMiraiApplication, logger
from graia.ariadne.model import Friend, MiraiSession as Session, Group, Member, UploadMethod
from graia.ariadne.event.message import FriendMessage, GroupMessage
from graia.ariadne.event.mirai import GroupRecallEvent, FriendRecallEvent
from graia.ariadne.message.element import Plain, At, Image, Face, AtAll, Source, Quote, FlashImage, Voice, Poke, MusicShare, File
