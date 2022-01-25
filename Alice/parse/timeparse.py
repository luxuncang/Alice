from datetime import datetime, timedelta
import asyncio, functools
from typing import Callable, Union, Optional, List, Dict, Any, BinaryIO, TextIO

def time_completion(date: str):
    date = date.strip().split()

    now_time = datetime.now()
    year = now_time.year
    month = now_time.month
    day = now_time.day

    def day_completion(date: list):
        if not ':' in date:
            return '时间格式错误!'
        if len(date.split(':')) == 3:
            date = datetime.strptime(date, '%H:%M:%S')
            return date.hour, date.minute, date.second
        elif len(date.split(':')) == 2:
            date = datetime.strptime(date, '%H:%M')
            return date.hour, date.minute, 0
        else:
            return 0, 0, 0

    if len(date) == 1:
        if not ':' in date[0]:
            return '时间格式错误!'
        if len(date[0].split(':')) == 3:
            date = datetime.strptime(date[0], '%H:%M:%S')
            return year, month, day, date.hour, date.minute, date.second
        elif len(date[0].split(':')) == 2:
            date = datetime.strptime(date[0], '%H:%M')
            return year, month, day, date.hour, date.minute, 0
        else:
            return year, month, day, 0, 0, 0
    elif len(date) == 2:
        if not '-' in date[0] and not ':' in date[1]:
            return '时间格式错误!'
        if len(date[0].split('-')) == 3:
            dates = datetime.strptime(date[0], '%Y-%m-%d')
            res = day_completion(date[1])
            if isinstance(res, str):
                return res
            return dates.year, dates.month, dates.day, *res
        elif len(date[0].split('-')) == 2:
            dates = datetime.strptime(date[0], '%m-%d')
            res = day_completion(date[1])
            if isinstance(res, str):
                return res
            return year, dates.month, dates.day, *res

class Timing:

    @staticmethod
    def conversion(date: str):
        if date[-1] in ('s', 'S', '秒'):
            return int(date[:-1])
        elif date[-1] in ('m', 'M', '分'):
            return int(date[:-1]) * 60
        elif date[-1] in ('h', 'H'):
            return int(date[:-1]) * 60 * 60
        elif date[-2:] in ('小时', '时'):
            return int(date[:-2]) * 60 * 60
        elif date[-1] in ('d', 'D', '天'):
            return int(date[:-1]) * 60 * 60 * 24
        elif date[-1] in ('w', 'W', '周'):
            return int(date[:-1]) * 60 * 60 * 24 * 7
        raise ValueError('时间格式错误!') 

    @staticmethod
    def completion(date: str):
        now = datetime.now()
        if ':' in date:
            res = date.split(':')
            if len(res) == 3:
                d = datetime(now.year, now.month, now.day, int(res[0]), int(res[1]), int(res[2]))
                date = d - datetime.now()
                print(date.seconds)
                if date.days < 0:
                    res = d + timedelta(days=1)
                    return True, (res - datetime.now()).seconds
                else:
                    return True, date.seconds
            elif len(res) == 2:
                d = datetime(now.year, now.month, now.day, int(res[0]), int(res[1]), 0)
                date = d - datetime.now()
                if date.days < 0:
                    res = d + timedelta(days=1)
                    return True, (res - datetime.now()).seconds
                else:
                    return True, date.seconds
        else:
            return False, sum([Timing.conversion(i) for i in date.split()])

    @classmethod
    def dispatch(cls, time):
        def func_wrapper(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                while True:
                    state, await_time = cls.completion(time)
                    await asyncio.sleep(await_time)
                    await func(*args, **kwargs)
                    if state:
                        await asyncio.sleep(1)
            return wrapper
        return func_wrapper
