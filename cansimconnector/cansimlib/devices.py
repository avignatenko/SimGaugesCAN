import logging
from typing import Callable

from . import canclient, common, xplaneclient

logger = logging.getLogger(__name__)


class Device:

    def __init__(self, sim: xplaneclient.XPlaneClient, can: canclient.CANClient):
        self._sim = sim
        self._can = can


class SingleValueIndicator(Device):

    async def _init_internal(
        self,
        can_id: int,
        port: int,
        dataref_str: str,
        idx,
        tolerance: float,
        freq: float = 5,
        dataref_to_value: Callable = lambda dataref: dataref,
    ):
        await self._sim.subscribe_dataref(
            dataref_str, idx, self._on_value_update, tolerance, freq
        )

        self._dataref_to_value = dataref_to_value
        self._can_id = can_id
        self._port = port

    async def _on_value_update(self, value):
        logger.debug("udpate received!! %s", value)
        await self._set_value(value)

    async def _set_value(self, value: float):
        await self._can.send(
            self._can_id,
            self._port,
            common.make_payload_float(self._dataref_to_value(value)),
        )
