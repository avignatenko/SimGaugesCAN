import logging

from .. import common
from ..devices import Device
from ..sim import Sim
from ..can import Can

logger = logging.getLogger(__name__)


class GyroSuction(Device):

    CAN_ID = 29

    async def init(self):
        await self._sim.subscribe_dataref(
            "sim/cockpit2/gauges/indicators/suction_1_ratio",
            None,
            self._on_suction_update,
            0.1,
            5,  # Hz
        )

    async def _on_suction_update(self, value):
        logger.debug("udpate received!! %s", value)
        await self._set_suction(value)

    async def _set_suction(self, value: float):
        await self._can.send(self.CAN_ID, 0, common.make_payload_float(value))
