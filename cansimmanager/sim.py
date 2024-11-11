import asyncio
import aiohttp
import json

from websockets.asyncio.client import connect, ClientConnection


class Sim:

    _wsclient: ClientConnection = None
    _httpsession: aiohttp.ClientSession = None

    async def _get_dataref_id(self, dataref: str) -> int:
        async with self._httpsession.get(
            f"/api/v1/datarefs?filter[name]={dataref}"
        ) as response:
            print(response.status)
            json = await response.json()
            print(json)
            return json["data"][0]["id"]

    async def connect(self, uri):
        self._httpsession = aiohttp.ClientSession(base_url=f"http://{uri}")
        self._wsclient = await connect(f"ws://{uri}/api/v1")
  
    async def get_updated_dataref(self) -> str:
        # for testing - never returning future
        # loop = asyncio.get_running_loop()
        # future = loop.create_future()
        # return await future
        data = await self._wsclient.recv()
        json = json.loads(data)
        # switch by message type
        if json["type"] == "dataref_update_values":
            dataref_id = 
        return data

    async def subscribe_datarefs(self, datarefs: list[str]) -> None:

        dataref_requests = []
        for dataref in datarefs:
            dataref_request = {"id": await self._get_dataref_id(dataref)}
            dataref_requests.append(dataref_request)

        request = {
            "req_id": 1,
            "type": "dataref_subscribe_values",
            "params": {"datarefs": dataref_requests},
        }

        await self._wsclient.send(json.dumps(request))

    def __del__(self):
        if self._wsclient:
            self._wsclient.close()
