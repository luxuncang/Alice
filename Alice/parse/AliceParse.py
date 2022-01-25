from ..internaltype import (
    MessageChain,
    Plain
)
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Dict, Iterable, Any, Tuple, Union
import re
from parse import parse, compile
from ..exception import ParseException

class Match(ABC):
    
    @abstractmethod
    def match(self):
        ...
    
class RegexMatch(Match):
    '''正则匹配'''
    
    def __init__(self, pattern: str) -> None:
        self.pattern = pattern
        
    def match(self, text: str) -> Iterable[str]:
        res = re.findall(self.pattern, text)
        if res:
            return res[0]
        return None

class ElementMatch(Match):
    '''元素匹配'''

    def __init__(self, *pattern: Iterable) -> Iterable:
        self.pattern = pattern
        
    def match(self, message: Any) -> Iterable[str]:
        res = []
        for p in self.pattern:
            r = message[p]
            if r:
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
        if self.pattern == message:
            return message
        return None

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
        res = self.pattern.parse(message)
        if res:
            return res

class ParseRusult:
    '''解析结果'''
    def __init__(self) -> None:
        self.command = []
        self.least = []
        self.options = []
        self.RegexMatch = []
        self.ElementMatch = []
        self.FullMatch = []
        self.ArgumentMatch = []
        self.ParseMatch = []

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
        raise AttributeError(name)

    @staticmethod
    def _reduction(parse_result):
        if isinstance(parse_result, list):
            if len(parse_result) == 1:
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
                res = cmd.match(self.distribution(cmd, message))
                if res:
                    self.result.command.append(res)
                    getattr(self.result, cmd.__class__.__name__).append(res)
                else:
                    raise ParseException()
                    
            for least in self.least:
                res = self.leastmatch(least, message)
                if res:
                    self.result.least += res
                else:
                    raise ParseException()
            
            for option in self.options:
                res = option.match(self.distribution(option, message))
                if res:
                    self.result.options.append(res)
                    getattr(self.result, option.__class__.__name__).append(res)

            return self.result
        except ParseException:
            return None

    @staticmethod
    def distribution(pattern: Match, message: MessageChain):
        if isinstance(pattern, (RegexMatch, ParseMatch)):
            return '\n'.join([i.text for i in message[Plain]])
        elif isinstance(pattern, (FullMatch, ArgumentMatch)):
            if pattern.type:
                return message[pattern.type]
            return message
        elif isinstance(pattern, ElementMatch):
            return message
    
    @staticmethod
    def strtoregex(pattern: Union[str, Match]) -> str:
        if isinstance(pattern, str):
            return RegexMatch(pattern)
        return pattern
    
    def leastmatch(self, least: Tuple[Iterable[Union[str, Match]], int], message: MessageChain) -> bool:
        result = []
        for i in least[0]:
            res = i.match(AliceParse.distribution(i, message))
            if res:
                getattr(self.result, i.__class__.__name__).append(res)
                result.append(res)
        if len(result) >= least[1]:
            return result
        return False
