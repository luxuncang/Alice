from ..internaltype import MessageChain, Forward, ForwardNode, Friend, Member
from typing import Union, List, Dict, Any, Optional, Callable, Tuple, TypeVar, Generic, Type, Iterator
from datetime import datetime

T = TypeVar('T', int, Friend, Member)

def obj_yield(obj: Any) -> Iterator[Any]:
    while True:
        yield obj

def batch_forwardnode(
    target: Union[List[T], T], 
    message: List[MessageChain] ,
    name: Union[List[str], str],
    time: Union[List[datetime], datetime] = None
    ):
    if isinstance(target, (int, Friend, Member)):
        target = obj_yield(target)
    if isinstance(name, str):
        name = obj_yield(name)
    if time is None:
        time = datetime.now()
    if isinstance(time, datetime):
        time = obj_yield(time)
    return Forward(*(ForwardNode(*i) for i in zip(target, time, message, name)))