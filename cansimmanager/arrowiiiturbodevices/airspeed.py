import logging

from .. import common
from ..devices import Device
from ..sim import Sim
from ..can import Can

logger = logging.getLogger(__name__)

class Airspeed(Device):

    CAN_ID = 16

    async def init(self):
        await self._sim.subscribe_dataref(
            "simcoders/rep/cockpit2/gauges/indicators/airspeed_kts_pilot",
            None,
            self._on_airspeed_update,
            0.05,
        )

    async def _on_airspeed_update(self, value):
        logger.debug("udpate received!! %s", value)
        await self._set_airpeed(value)

    async def _set_airpeed(self, value: float):
        await self._can.send(self.CAN_ID, 0, common.make_payload_float(value))
