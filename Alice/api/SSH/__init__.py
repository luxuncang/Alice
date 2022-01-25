import paramiko
import asyncio
import threading
import sys
from typing import Callable

class ParamikoClient:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.loop = asyncio.get_event_loop()
        self.ssh = None
        self.channel = None
        self.task = None
        self.queue = []

    async def __aenter__(self) -> "ParamikoClient":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.t.join(0.1)
        self.ssh.close()
    
    async def connect(self):
        trans = paramiko.Transport((self.host, self.port))
        trans.connect(username=self.username, password=self.password)

        # 将sshclient的对象的transport指定为以上的trans
        self.ssh = paramiko.SSHClient()
        self.ssh._transport = trans

        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.channel = self.ssh.invoke_shell()
        self.t = threading.Thread(target=self.channel_recv)
        self.t.start()
        # self.loop.create_task(self.send())
    
    async def send(self):
        n = 0
        while True:
            n1 = len(self.queue)
            if n1 > n:
                res = self.queue[n:n1]
                n = n1
                return res
            else:
                await asyncio.sleep(1)

    def channel_recv(self):
        while True:
            text = self.channel.recv(1024)
            if text:
                self.queue += text.decode().split('\n')
    
    async def cmd(self, text: str):
        self.channel.send(text + '\n')
        await asyncio.sleep(1)
