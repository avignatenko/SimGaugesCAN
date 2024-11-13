import logging

from .. import common
from ..devices import Device
from ..sim import Sim
from ..can import Can

logger = logging.getLogger(__name__)


class Attitude(Device):

    CAN_ID = 28

    async def init(self):
        await self._sim.subscribe_dataref(
            "simcoders/rep/cockpit2/gauges/indicators/attitude_indicator_0_roll",
            None,
            self._on_roll_update,
            0.05,          
        )

        await self._sim.subscribe_dataref(
            "simcoders/rep/cockpit2/gauges/indicators/attitude_indicator_0_pitch",
            None,
            self._on_pitch_update,
            0.05,          
        )

    async def _on_roll_update(self, value):
        logger.debug("udpate received!! %s", value)
        await self._set_roll(value)

    async def _set_roll(self, value: float):
        await self._can.send(self.CAN_ID, 1, common.make_payload_float(value))

    async def _on_pitch_update(self, value):
        logger.debug("udpate received!! %s", value)
        await self._set_pitch(value)

    async def _set_pitch(self, value: float):
        await self._can.send(self.CAN_ID, 0, common.make_payload_float(value))
