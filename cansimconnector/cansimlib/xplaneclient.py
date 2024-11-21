import asyncio
import json
import logging
import time
from typing import Callable

import aiohttp
from websockets.asyncio.client import ClientConnection, connect

logger = logging.getLogger(__name__)


class XPlaneClient:

    class DatarefData:
        class CallbackData:
            def __init__(self, callback: Callable, tolerance: float, freq: float):
                self.callback = callback
                self.tolerance = tolerance
                self.freq = freq
                self.last_value = None
                self.last_update_time = None
                self.update_task = None

        def __init__(self):
            self.value = None
            self.last_update_time = None
            self.update_callbacks = []

    def __init__(self):
        self._wsclient: ClientConnection = None
        self._httpsession: aiohttp.ClientSession = None
        self._datarefsStorage: dict[int, self.DatarefData] = {}

    async def _wait_and_call_callback(self, time_to_update, dataref, callback):
        if time_to_update > 0:
            await asyncio.sleep(time_to_update)

        value2 = dataref.value[0] if len(dataref.value) == 1 else dataref.value

        callback.last_update_time = time.time()
        callback.last_value = dataref.value

        await callback.callback(value2)

    async def _process_single_callback_update(self, dataref, callback):

        # changed enough?
        if callback.last_value:
            small_change = True
            for last_value, value in zip(callback.last_value, dataref.value):
                small_change = abs(last_value - value) < callback.tolerance
                if not small_change:
                    break
            if small_change:
                return

        if callback.update_task is not None and not callback.update_task.done():
            return

        # let's figure out when to update next time
        time_to_next_update = 0
        if callback.last_update_time:
            time_to_next_update = (
                callback.last_update_time + (1.0 / callback.freq) - time.time()
            )

        callback.update_task = asyncio.create_task(
            self._wait_and_call_callback(0, dataref, callback)
        )

    # await callback.update_task

    async def _process_single_dataref_update(self, dataref_id, value):
        dataref = self._datarefsStorage.get(dataref_id)
        if not dataref:
            logger.warning("Received unknown dataref %s", dataref_id)
            return

        if not isinstance(value, list):
            value = [value]

        dataref.value = value

        # now iterate over callbacks

        callbacks_processes = [
            asyncio.create_task(self._process_single_callback_update(dataref, callback))
            for callback in dataref.update_callbacks
        ]
        await asyncio.gather(*callbacks_processes)

    async def _process_datarefs_update_2(self, data):
        datarefs_processes = [
            asyncio.create_task(
                self._process_single_dataref_update(int(dataref_id_str), value)
            )
            for dataref_id_str, value in data.items()
        ]
        await asyncio.gather(*datarefs_processes)

    async def connect(self, uri):
        try:
            self._httpsession = aiohttp.ClientSession(
                base_url=f"http://{uri}", timeout=aiohttp.ClientTimeout(total=10)
            )
            self._wsclient = await connect(f"ws://{uri}/api/v1")
        except (OSError, TimeoutError):
            if self._httpsession is not None:
                await self._httpsession.close()
            if self._wsclient is not None:
                await self._wsclient.close()
            raise

    async def get_dataref_id(self, dataref: str) -> int:
        async with self._httpsession.get(
            f"/api/v1/datarefs?filter[name]={dataref}"
        ) as response:
            json = await response.json()
            id = json["data"][0]["id"]
            logger.debug("Dataref %s ID is %s", dataref, id)
            return id

    async def send_dataref(self, dataref_id: int, index, dataref_value) -> None:

        dataref_value = {"id": dataref_id, "value": dataref_value}
        if index is not None:
            dataref_value["index"] = index

        update_request = {
            "req_id": 2,
            "type": "dataref_set_values",
            "params": {"datarefs": [dataref_value]},
        }
        await self._wsclient.send(json.dumps(update_request))

    async def subscribe_dataref(
        self,
        dataref: str,
        index,
        callback: Callable,
        tolerance: float,
        freq: float = 10,
    ) -> None:

        dataref_id = await self.get_dataref_id(dataref)

        dataref_subscription = {"id": dataref_id}
        if index is not None:
            dataref_subscription["index"] = index

        subscribe_request = {
            "req_id": 1,
            "type": "dataref_subscribe_values",
            "params": {"datarefs": [dataref_subscription]},
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
                    await self._process_datarefs_update_2(data_json["data"])
                case "result":
                    if data_json["success"] == False:
                        logger.error(
                            "WS error returned for request %s", data_json["req_id"]
                        )

    def __del__(self):
        if self._wsclient:
            self._wsclient.close()