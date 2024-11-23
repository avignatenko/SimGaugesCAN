import asyncio
import logging
import time

from .. import cansimlib

logger = logging.getLogger(__name__)


class Airspeed(cansimlib.Device):

    CAN_ID = 16

    async def init(self):
        await self._sim.subscribe_dataref(
            "simcoders/rep/cockpit2/gauges/indicators/airspeed_kts_pilot",
            None,
            self._on_airspeed_update,
            0.01,
        )

    async def _on_airspeed_update(self, value):
        logger.debug("udpate received!! %s", value)
        await self._set_airpeed(value)

    async def _set_airpeed(self, value: float):
        await self._can.send(self.CAN_ID, 0, cansimlib.make_payload_float(value))


class Dataref:
    def __init__(self, sim, dt, tolerance=0.01):
        self._dt = dt
        self._tolerance = tolerance
        self._sim = sim
        self._prev_value = None

    @classmethod
    async def create(cls, sim, dataref_str, tolerance=0.01):
        dt = await sim.subscribe_dataref_no_callback(dataref_str)
        self = cls(sim, dt, tolerance)
        return self

    async def get_value(self):
        while True:
            value = await self._sim.wait_dataref(self._dt)
            if self._prev_value and abs(self._prev_value - value[0]) < self._tolerance:
                continue
            self._prev_value = value[0]
            return value


class Airspeed2(cansimlib.Device):

    async def create_dataref(self, dataref_str, tolerance=0.01):
        return await Dataref.create(
            self._sim,
            dataref_str,
            tolerance,
        )

    async def run_sim(self):
        v = self.create_dataref(
            "simcoders/rep/cockpit2/gauges/indicators/airspeed_kts_pilot"
        )

        while True:
            value = await v.get_value()
            await self._can.send(16, 0, cansimlib.make_payload_float(value[0]))
