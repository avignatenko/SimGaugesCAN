import asyncio
import logging

from . import common
from .devices import Device
from .sim import Sim
from .can import Can

logger = logging.getLogger(__name__)


class GyroSuction(Device):

    CAN_ID = 29

    def __init__(self, sim: Sim, can: Can):
        self._sim = sim
        self._can = can

    async def init(self):
        await self._sim.subscribe_dataref(
            "sim/cockpit2/gauges/indicators/suction_1_ratio",
            0.1,
            5,  # Hz
            self._on_suction_update,
        )

    async def _on_suction_update(self, value):
        logging.debug("udpate received!! %s", value)
        await self._set_suction(value)

    async def _set_suction(self, value: float):
        await self._can.send(self.CAN_ID, 0, common.make_payload_float(value))

class Airspeed(Device):

    CAN_ID = 16

    def __init__(self, sim: Sim, can: Can):
        self._sim = sim
        self._can = can

    async def init(self):
        await self._sim.subscribe_dataref(
            "simcoders/rep/cockpit2/gauges/indicators/airspeed_kts_pilot",
            0.05,
            10,  # Hz
            self._on_airspeed_update,
        )

    async def _on_airspeed_update(self, value):
        logging.debug("udpate received!! %s", value)
        await self._set_airpeed(value)

    async def _set_airpeed(self, value: float):
        await self._can.send(self.CAN_ID, 0, common.make_payload_float(value))


_devices: list[Device] = []

def register(sim: Sim, can: Can):
    _devices.append(GyroSuction(sim, can))
    _devices.append(Airspeed(sim, can))

async def init():
    for device in _devices:
        await device.init()
