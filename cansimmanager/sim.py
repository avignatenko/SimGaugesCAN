import asyncio
import logging
import aiohttp
import json
import time

from typing import Callable

from websockets.asyncio.client import connect, ClientConnection

logger = logging.getLogger(__name__)


class Sim:

    class DatarefData:
        class CallbackData:
            def __init__(self, callback: Callable, tolerance: float, freq: float):
                self.callback = callback
                self.tolerance = tolerance
                self.freq = freq
                self.last_value = None
                self.last_update_time = None

        def __init__(self):
            self.value = None
            self.update_callbacks = []

    def __init__(self):
        self._wsclient: ClientConnection = None
        self._httpsession: aiohttp.ClientSession = None
        self._datarefsStorage: dict[int, self.DatarefData] = {}

    async def _get_updated_dataref(self) -> str:
        # for testing - never returning future
        # loop = asyncio.get_running_loop()
        # future = loop.create_future()
        # return await future
        data = await self._wsclient.recv()
        json = json.loads(data)
        # switch by message type
        if json["type"] == "dataref_update_values":
            dataref_id = 1
        return data

    async def _process_dataref_update(self, data):
        for dataref_id_str, value in data.items():
            dataref = self._datarefsStorage.get(int(dataref_id_str))
            if not dataref:
                continue

            dataref.value = value
            cur_time = time.time()
            for callback in dataref.update_callbacks:
                if (
                    callback.last_value
                    and abs(callback.last_value - value) < callback.tolerance
                ):
                    continue

                if (
                    callback.last_update_time
                    and cur_time - callback.last_update_time < (1.0 / callback.freq)
                ):
                    continue

                callback.last_update_time = cur_time
                callback.last_value = value
                task = asyncio.create_task(callback.callback(value))

    async def connect(self, uri):
        self._httpsession = aiohttp.ClientSession(base_url=f"http://{uri}")
        self._wsclient = await connect(f"ws://{uri}/api/v1")

    async def get_dataref_id(self, dataref: str) -> int:
        async with self._httpsession.get(
            f"/api/v1/datarefs?filter[name]={dataref}"
        ) as response:
            json = await response.json()
            return json["data"][0]["id"]

    async def send_dataref(self, dataref_id: int, dataref_value) -> None:
        update_request = {
            "req_id": 2,
            "type": "dataref_set_values",
            "params": {"datarefs": [{"id": dataref_id, "value": dataref_value}]},
        }
        await self._wsclient.send(json.dumps(update_request))

    async def subscribe_dataref(
        self, dataref: str, callback: Callable, tolerance: float, freq: float = 10
    ) -> None:

        dataref_id = await self.get_dataref_id(dataref)
        subscribe_request = {
            "req_id": 1,
            "type": "dataref_subscribe_values",
            "params": {"datarefs": [{"id": dataref_id}]},
        }

        await self._wsclient.send(json.dumps(subscribe_request))

        callback_data = self.DatarefData.CallbackData(callback, tolerance, freq)

        dataref_data = self._datarefsStorage.setdefault(dataref_id, self.DatarefData())
        dataref_data.update_callbacks.append(callback_data)

    async def run(self) -> None:
        # process:
        # - wait for the message
        # - process the message
        logger.info("Starting WebSockets handler")
        while True:
            data = await self._wsclient.recv(decode=False)
            data_json = json.loads(data)
            # switch by message type
            match data_json["type"]:
                case "dataref_update_values":
                    asyncio.create_task(self._process_dataref_update(data_json["data"]))
                case "result":
                    if data_json["success"] == False:
                            logger.error("WS error returned for request %s", data_json["req_id"])

    def __del__(self):
        if self._wsclient:
            self._wsclient.close()
