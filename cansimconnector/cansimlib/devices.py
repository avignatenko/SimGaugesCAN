import asyncio
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


class Dataref:
    def __init__(self, sim, dt, index: list | None, tolerance=0.01):
        self._dt = dt
        self._index = index
        self._tolerance = tolerance
        self._sim: xplanewsclient.XPlaneClient = sim
        self._prev_value = None

    @classmethod
    async def create(cls, sim, dataref_str, index: list | None, tolerance=0.01):
        dt = await sim.subscribe_dataref_no_callback(dataref_str)
        self = cls(sim, dt, index, tolerance)
        return self

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
            value = self._sim.get_dataref(self._dt)
            if value is not None:
                # remove unused
                if self._index:
                    value = [value[i] for i in self._index]

                if not self._is_small_change(value):
                    self._prev_value = value
                    return value[0] if len(value) == 1 else value

            await self._sim.receive_new_dataref(self._dt)


class Device2:
    def __init__(self, sim: xplanewsclient.XPlaneClient, can: canclient.CANClient):
        self._sim = sim
        self._can = can

    async def create_dataref(
        self, dataref_str, index: list[int] | None = None, tolerance=0.01
    ):
        return await Dataref.create(
            self._sim,
            dataref_str,
            index,
            tolerance,
        )

    async def run_sim(self):
        pass

    async def run_can(self):
        pass

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.run_sim())
            tg.create_task(self.run_can())


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
