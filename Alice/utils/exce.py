import threading, asyncio

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