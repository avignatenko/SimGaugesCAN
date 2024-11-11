import logging

from .. import common
from ..devices import Device
from ..sim import Sim
from ..can import Can

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