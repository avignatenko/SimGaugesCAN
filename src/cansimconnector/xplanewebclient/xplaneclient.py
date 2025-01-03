from __future__ import annotations

import asyncio
import json
import logging

import aiohttp
# from websockets.asyncio.client import ClientConnection, connect

logger = logging.getLogger(__name__)


class DatarefSubscription:
    def __init__(self, sim, dataref_id, index: list | None, tolerance=0.01):
        self._datatef_id = dataref_id
        self._index = index
        self._tolerance = tolerance
        self._sim: XPlaneClient = sim
        self._prev_value = None

    @classmethod
    async def create(cls, sim, dataref_str, index: list | None, tolerance=0.01):
        dataref_id = await sim.subscribe_dataref(dataref_str)
        return cls(sim, dataref_id, index, tolerance)

    def _is_small_change(self, new_value: list):
        if not self._prev_value or not self._tolerance:
            return False

        small_change = True

        for prev_value, value in zip(self._prev_value, new_value):
            small_change = abs(prev_value - value) < self._tolerance
            if not small_change:
                break

        return small_change

    def get_value(self):
        value = self._prev_value
        if value is None:
            return value
        return value[0] if len(value) == 1 else value

    async def receive_new_value(self):
        while True:
            value = self._sim.get_dataref(self._datatef_id)
            if value is not None:
                # remove unused
                if self._index:
                    value = [value[i] for i in self._index]

                if not self._is_small_change(value):
                    self._prev_value = value
                    return self.get_value()

            await self._sim.receive_new_dataref(self._datatef_id)


class XPlaneClient:
    class DatarefData:
        def __init__(self):
            self.value = None
            self.value_future = asyncio.get_running_loop().create_future()

    def __init__(self):
        #     self._wsclient: ClientConnection = None
        self._wssession: aiohttp.ClientWebSocketResponse = None
        self._httpsession: aiohttp.ClientSession = None
        self._datarefs_storage: dict[int, self.DatarefData] = {}

    async def _process_single_dataref_update(self, dataref_id, value):
        dataref = self._datarefs_storage.get(dataref_id)
        if not dataref:
            logger.warning("Received unknown dataref %s", dataref_id)
            return

        # always return list, even for singular items
        if not isinstance(value, list):
            value = [value]

        dataref.value = value
        dataref.value_future.set_result(value)
        dataref.value_future = asyncio.get_running_loop().create_future()

    async def _process_datarefs_update(self, data):
        async with asyncio.TaskGroup() as tg:
            for dataref_id_str, value in data.items():
                tg.create_task(self._process_single_dataref_update(int(dataref_id_str), value))

    async def connect(self, uri):
        try:
            self._httpsession = aiohttp.ClientSession(
                base_url=f"http://{uri}", timeout=aiohttp.ClientTimeout(total=100)
            )
            # self._wssession = self._httpsession.ws_connect(f"ws://{uri}/api/v1")

            self._wssession = await self._httpsession.ws_connect("/api/v1")

            # no compression, no ping for performance (maybe reconsider)
            # self._wsclient = await connect(f"ws://{uri}/api/v1", compression=None, ping_interval=None)
        except (OSError, TimeoutError):
            if self._httpsession is not None:
                await self._httpsession.close()
            # if self._wsclient is not None:
            #    await self._wsclient.close()
            raise

    async def get_dataref_id(self, dataref: str) -> int:
        async with self._httpsession.get(f"/api/v1/datarefs?filter[name]={dataref}") as response:
            response_json = await response.json()
            dataref_id = response_json["data"][0]["id"]
            logger.debug("Dataref %s ID is %s", dataref, dataref_id)
            return dataref_id

    async def send_dataref(self, dataref_id: int, dataref_value) -> None:
        self.send_dataref_idx(dataref_id, None, dataref_value)

    async def send_dataref_idx(self, dataref_id: int, index, dataref_value) -> None:
        dataref_value = {"id": dataref_id, "value": dataref_value}
        if index is not None:
            dataref_value["index"] = index

        update_request = {
            "req_id": 2,
            "type": "dataref_set_values",
            "params": {"datarefs": [dataref_value]},
        }
        # await self._wsclient.send(json.dumps(update_request))
        self._wssession.send_json(update_request)

    def get_dataref(self, dataref_id: int):
        return self._datarefs_storage.get(dataref_id).value

    def receive_new_dataref(self, dataref_id: int):
        return self._datarefs_storage.get(dataref_id).value_future

    async def _subsribe_and_get_dataref_data(self, dataref_id: int, idx: int | None):
        # subscribed already? (fixme - need to deal with freq)
        if dataref_id not in self._datarefs_storage:
            dataref_subscription = {"id": dataref_id}
            if idx is not None:
                dataref_subscription["index"] = idx
            subscribe_request = {
                "req_id": 1,
                "type": "dataref_subscribe_values",
                "params": {"datarefs": [dataref_subscription]},
            }

            # await self._wsclient.send(json.dumps(subscribe_request))
            self._wssession.send_json(subscribe_request)

            self._datarefs_storage[dataref_id] = self.DatarefData()

        return self._datarefs_storage[dataref_id]

    async def subscribe_dataref(self, dataref: str, freq: float = 10) -> int:
        del freq  # unused

        dataref_id = await self.get_dataref_id(dataref)
        await self._subsribe_and_get_dataref_data(dataref_id, None)
        return dataref_id

    async def run(self) -> None:
        # process:
        # - wait for the message
        # - process the message
        logger.info("Starting WebSockets handler")

        while True:
            # data = await self._wsclient.recv(decode=False)
            # data_json = json.loads(data)

            data_json = await self._wssession.receive_json()

            # switch by message type
            match data_json["type"]:
                case "dataref_update_values":
                    await self._process_datarefs_update(data_json["data"])
                case "result":
                    if data_json["success"] is False:
                        logger.error("WS error returned for request %s", data_json["req_id"])


#    def __del__(self):
#        if self._wsclient:
#            self._wsclient.close()
