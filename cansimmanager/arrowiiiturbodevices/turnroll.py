import logging

from .. import common
from ..devices import Device
from ..sim import Sim
from ..can import Can

from .gyrosuction import GyroSuction

logger = logging.getLogger(__name__)


class TurnRoll(Device):

    CAN_ID = 19

    async def init(self):
        await self._sim.subscribe_dataref(
            "sim/cockpit2/gauges/indicators/slip_deg",
            None,
            self._on_slip_deg_update,
            0.01,
        )

        await self._sim.subscribe_dataref(
            "sim/cockpit2/gauges/indicators/turn_rate_roll_deg_pilot",
            None,
            self._on_turn_rate_update,
            0.1,
        )

    async def _on_slip_deg_update(self, value):
        logger.debug("udpate received!! %s", value)
        await self._set_slip_deg(value)

    async def _set_slip_deg(self, value: float):
        await self._can.send(self.CAN_ID, 1, common.make_payload_float(-value * 3))

    async def _on_turn_rate_update(self, value):
        logger.debug("udpate received!! %s", value)
        await self._set_turn_rate(value)

    async def _set_turn_rate(self, value: float):
        await self._can.send(self.CAN_ID, 0, common.make_payload_float(value))
