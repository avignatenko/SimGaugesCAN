import asyncio

from websockets.asyncio.client import connect, ClientConnection


class Sim:

    _wsclient: ClientConnection = None

    async def connect(self, uri):
        self._wsclient = await connect(uri)

    async def get_updated_dataref(self) -> str:
        # for testing - never returning future
        # loop = asyncio.get_running_loop()
        # future = loop.create_future()
        #  return await future
        data = await self._wsclient.recv()
        return data

    def __del__(self):
        if self._wsclient:
            self._wsclient.close()
