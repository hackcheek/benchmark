from __future__ import annotations
import abc
import asyncio

from web3 import AsyncWeb3
from typing import Iterable
from web3.providers import WebsocketProviderV2


class Listener(abc.ABC):
    @abc.abstractmethod
    def __init__(self, rpc_url: str, polling_time: float = 0.1):
        self.w3: AsyncWeb3

    @abc.abstractmethod
    def __aiter__(self) -> Listener:
        return self
    
    @abc.abstractmethod
    async def __anext__(self) -> Iterable:


class WebSocketListener(Listener):
    def __init__(self, rpc_url: str, polling_time: float = 0.1):
        self.polling_time = polling_time
        self.w3 = AsyncWeb3.persistent_websocket(WebsocketProviderV2(rpc_url))
        loop = asyncio.get_running_loop()
        self.subscription_id = None
        self.events = []
        
    def __aiter__(self):
        return self

    async def __anext__(self) -> Iterable:
        event = await self.w3.ws.listen_to_websocket().__anext__()
        return [event]


class WebSocketContractListener(Listener):
    def __init__(self, rpc_url: str, polling_time: float = 0.1):
        self.polling_time = polling_time
        self.w3 = AsyncWeb3.persistent_websocket(WebsocketProviderV2(rpc_url))
        loop = asyncio.get_running_loop()
        self.subscription_id = None
        self._setup = loop.create_task(self.setup())
        self.events = []
        
    def __aiter__(self):
        return self

    async def __anext__(self) -> Iterable:
        event = await self.w3.ws.listen_to_websocket().__anext__()
        return [event]

    async def setup(self):
        if self._setup and self._setup.done():
            return self
        if not await self.w3.is_connected():
            await self.w3.provider.connect()
        self.subscription_id = await self.w3.eth.subscribe(
            "logs", {
                "address": self.node.task_runner.address,
                "topics": [self.w3.keccak(text="TaskAdded(uint256,string,string)")]
            }
        )
        return self


class HTTPListener(Listener):
    ...
