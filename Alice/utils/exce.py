import threading, asyncio, inspect, functools
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# 重写可返回的线程
class Thread(threading.Thread):
    '''Thread method(可返回)'''

    def run(self):
        try:
            if self._target:
                self.__state = True
                try:
                    self.results = self._target(*self._args, **self._kwargs)
                except Exception as e:
                    self.results = str(e)
                self.__state = False
        finally:
            del self._target, self._args, self._kwargs

    def result(self):
        try:
            return self.results
        except Exception:
            return None
    
    async def start(self):
        super().start()
        while self.__state:
            await asyncio.sleep(1)
        return self.result()

# 创建loop任务
def loop_task(loop = None):
    def task(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not loop:
                loops = asyncio.get_event_loop()
                task = loops.create_task(func(*args, **kwargs))
                return task
            return loop.create_task(func(*args, **kwargs))
        return wrapper
    return task

# 递归调用
def recursion(func, args, n = 1):
    for i in range(n):
        args = func(args)
    return args

# 捕获 exec 输出(线程不安全, 影响全局sys.stdout, sys.stderr)
def get_exec(code: str):
    f = StringIO()
    with redirect_stdout(f), redirect_stderr(f):
        exec(code)
    s = f.getvalue()
    return s