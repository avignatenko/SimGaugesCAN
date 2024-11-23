import enum
import logging
from dataclasses import dataclass
from typing import Callable

from . import canclient, common, xplanewsclient

logger = logging.getLogger(__name__)


class Device:
    def __init__(self, sim: xplanewsclient.XPlaneClient, can: canclient.CANClient):
        self._sim = sim
        self._can = can


class PhysicalSwitch(Device):
    def __init__(
        self,
        sim: xplanewsclient.XPlaneClient,
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
    class CANType(enum.Enum):
        FLOAT = 1
        BYTE = 2

    @dataclass
    class DatarefSubsription:
        dataref_str: str
        idx: int | None = None
        tolerance: float = 0.01
        freq: float = 10

    def __init__(
        self,
        sim: xplanewsclient.XPlaneClient,
        can: canclient.CANClient,
        can_id: int,
        port: int,
        datarefs: list[DatarefSubsription],
        dataref_to_value: Callable = lambda value: value,
        type: CANType = CANType.FLOAT,
    ):
        super().__init__(sim, can)

        self._vars = [None] * len(datarefs)
        self._dataref_to_value = dataref_to_value
        self._can_id = can_id
        self._port = port
        self._dataref_subscription = datarefs

        match type:
            case SingleValueIndicator.CANType.FLOAT:
                self._set_value_func = self._set_value_float
            case SingleValueIndicator.CANType.BYTE:
                self._set_value_func = self._set_value_byte

    async def init(self):
        for i, s in enumerate(self._dataref_subscription):
            await self._sim.subscribe_dataref(
                dataref=s.dataref_str,
                idx=s.idx,
                callback=self._on_value_update,
                tolerance=s.tolerance,
                freq=s.freq,
                context=i,
            )

    async def _on_value_update(self, value, idx):
        logger.debug("update received!! %s %s", idx, value)
        self._vars[idx] = value
        if None in self._vars:
            return
        await self._set_value_func(*self._vars)

    async def _set_value_float(self, *values):
        await self._can.send(
            self._can_id,
            self._port,
            common.make_payload_float(self._dataref_to_value(*values)),
        )

    async def _set_value_byte(self, *values):
        await self._can.send(
            self._can_id,
            self._port,
            common.make_payload_byte(self._dataref_to_value(*values)),
        )
