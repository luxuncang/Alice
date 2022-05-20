from ..internaltype import (
    MessageChain,
    Plain
)
from abc import ABC, abstractmethod
from typing import Dict, Iterable, Any, Tuple, Union
import re
from parse import parse, compile
from typefire import typeswitch, typefire, TypeFire
from pydantic import create_model, BaseModel
from ..exception import ParseException

TypeFire.capture_fire()

class Match(ABC):
    
    @abstractmethod
    def match(self):
        ...
    
class RegexMatch(Match):
    '''正则匹配'''
    
    def __init__(self, pattern: str) -> None:
        self.pattern = pattern
        
    def match(self, text: str) -> Iterable[str]:
        return res[0] if (res := re.findall(self.pattern, text)) else None

class ElementMatch(Match):
    '''元素匹配'''

    def __init__(self, *pattern: Iterable) -> Iterable:
        self.pattern = pattern
        
    def match(self, message: Any) -> Iterable[str]:
        res = []
        for p in self.pattern:
            if r := message[p]:
                res+=r
            else:
                return None
        return res

class FullMatch(Match):
    '''完全匹配'''

    def __init__(self, pattern: Any, type = None) -> None:
        self.pattern = pattern
        self.type = type

    def match(self, message: Any) -> Any:
        return message if self.pattern == message else None

class ArgumentMatch(Match):
    '''参数匹配'''
    
    def __init__(self, pattern: Dict[str, Any], type = None) -> None:
        self.pattern = pattern
        self.type = type
    
    def match(self, message: Any) -> Any:
        if message:
            for i in message:
                for k, v in self.pattern.items():
                    if getattr(i, k) != v:
                        raise ParseException()
                return i
        return None

class ParseMatch(Match):
    '''解析结果'''
    
    def __init__(self, pattern: str) -> None:
        self.pattern = compile(pattern)
    
    def match(self, message: str) -> Iterable[str]:
        if res := self.pattern.parse(message):
            return res 

class FireMatch(Match):
    '''fire解析'''

    def __init__(self, signature: Dict[str, tuple]) -> None:
        self.f = self.generat_func(signature)

    def match(self, message: str):
        if res := typefire(self.f)(message):
            return res
        
    def generat_func(self, signature: dict):
        s = 'def _('
        def hint(v):
            if len(v) <= 1:
                v = (..., ...)
            h = ''
            if v[0] == ... or v[0] is None:
                ...
            else:
                h += f': {v[0] if isinstance(v[0], str) else v[0].__name__}'
            if v[1] == ...:
                ...
            else:
                h += f' = {v[1]}'
            h += ','
            return h

        for k,v in signature.items():
            s += k + hint(v)
        s += '):\n    return locals()'
        s += '\nTemp.f = _'
        class Temp:
            ...
        exec(s)
        return Temp.f

class ParseRusult:
    '''解析结果'''
    def __init__(self, message: MessageChain = None) -> None:
        self.command = []
        self.least = []
        self.options = []
        self.RegexMatch = []
        self.ElementMatch = []
        self.FullMatch = []
        self.ArgumentMatch = []
        self.ParseMatch = []
        self.FireMatch = []
        self.message = message

    def __getattr__(self, name):
        if name == 'cmd':
            return self._reduction(self.command)
        elif name == 'lat':
            return self._reduction(self.least)
        elif name == 'opt':
            return self._reduction(self.options)
        elif name == 're':
            return self._reduction(self.RegexMatch)
        elif name == 'ele':
            return self._reduction(self.ElementMatch)
        elif name == 'full':
            return self._reduction(self.FullMatch)
        elif name == 'arg':
            return self._reduction(self.ArgumentMatch)
        elif name == 'par':
            return self._reduction(self.ParseMatch)
        else:
            for i in self.ParseMatch:
                if name in i.named:
                    return i[name]
            for i in self.FireMatch:
                if name in i:
                    return i[name]
        # raise AttributeError(name)
        return None

    def get_dict(self):
        data = {}
        for i in self.ParseMatch:
            data |= i.named
        return {
            'cmd': self.cmd,
            'lat': self.lat,
            'opt': self.opt,
            're': self.re,
            'ele': self.ele,
            'full': self.full,
            'arg': self.arg,
            'par': self.par,
            **data
        }

    @staticmethod
    def _reduction(parse_result):
        if isinstance(parse_result, list) and len(parse_result) == 1:
            return parse_result[0]
        return parse_result


class AliceParse(Match):

    def __init__(
        self, 
        command: Iterable[Union[str, Match]], 
        least: Iterable[Tuple[Iterable[Union[str, Match]], int]] = [],
        options: Iterable[Union[str, Match]] = []
        ) -> None:
        self.command = list(map(self.strtoregex, command))
        self.least = [(list(map(self.strtoregex, i[0])), i[1]) for i in least]
        self.options = list(map(self.strtoregex, options))
    
    def match(self, message: MessageChain):
        '''
        * 条件匹配
        * 解析匹配
        '''
        self.result = ParseRusult()
        try:
            for cmd in self.command:
                if res := cmd.match(self.distribution(cmd, message)):
                    self.result.command.append(res)
                    getattr(self.result, cmd.__class__.__name__).append(res)
                else:
                    raise ParseException()

            for least in self.least:
                if res := self.leastmatch(least, message):
                    self.result.least += res
                else:
                    raise ParseException()

            for option in self.options:
                if res := option.match(self.distribution(option, message)):
                    self.result.options.append(res)
                    getattr(self.result, option.__class__.__name__).append(res)

            return self.result
        except ParseException:
            return None

    @staticmethod
    def distribution(pattern: Match, message: MessageChain):
        if isinstance(pattern, (RegexMatch, ParseMatch, FireMatch)):
            return '\n'.join([i.text for i in message[Plain]])
        elif isinstance(pattern, (FullMatch, ArgumentMatch)):
            if pattern.type:
                return message[pattern.type]
            return message
        elif isinstance(pattern, ElementMatch):
            return message
    
    @staticmethod
    def strtoregex(pattern: Union[str, Match]) -> str:
        return RegexMatch(pattern) if isinstance(pattern, str) else pattern
    
    def leastmatch(self, least: Tuple[Iterable[Union[str, Match]], int], message: MessageChain) -> bool:
        result = []
        for i in least[0]:
            if res := i.match(AliceParse.distribution(i, message)):
                getattr(self.result, i.__class__.__name__).append(res)
                result.append(res)
        if len(result) >= least[1]:
            return result
        return False
