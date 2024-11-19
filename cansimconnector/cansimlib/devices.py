import logging
from typing import Callable

from . import canclient, common, xplaneclient

logger = logging.getLogger(__name__)


class Device:

    def __init__(self, sim: xplaneclient.XPlaneClient, can: canclient.CANClient):
        self._sim = sim
        self._can = can


class PhysicalSwitch(Device):

    def __init__(
        self,
        sim: xplaneclient.XPlaneClient,
        can: canclient.CANClient,
        can_id: int,
        port: int,
        dataref_str: str,
        idx,
        payload_to_dataref: Callable = lambda dataref: dataref,
    ):
        super().__init__(sim, can)
        self._port = port
        self._idx = idx
        self._can_id = can_id
        self._dataref_str = dataref_str
        self._payload_to_dataref = payload_to_dataref

    async def init(self):
        self._dataref_id = await self._sim.get_dataref_id(self._dataref_str)
        await self._can.subscribe_message(self._can_id, self._on_can_message)

    async def _on_can_message(self, port, payload):
        if port != self._port:
            return

        dataref_value = self._payload_to_dataref(payload)

        await self._sim.send_dataref(self._dataref_id, self._idx, dataref_value)


class SingleValueIndicator(Device):

    def __init__(
        self,
        sim: xplaneclient.XPlaneClient,
        can: canclient.CANClient,
        can_id: int,
        port: int,
        dataref_str: str,
        idx,
        tolerance: float,
        freq: float = 5,
        dataref_to_value: Callable = lambda dataref: dataref,
    ):
        super().__init__(sim, can)

        self._dataref_to_value = dataref_to_value
        self._can_id = can_id
        self._port = port
        self._dataref_str = dataref_str
        self._idx = idx
        self._tolerance = tolerance
        self._freq = freq

    async def init(self):
        await self._sim.subscribe_dataref(
            self._dataref_str,
            self._idx,
            self._on_value_update,
            self._tolerance,
            self._freq,
        )

    async def _on_value_update(self, value):
        logger.debug("udpate received!! %s", value)
        await self._set_value(value)

    async def _set_value(self, value: float):
        await self._can.send(
            self._can_id,
            self._port,
            common.make_payload_float(self._dataref_to_value(value)),
        )
