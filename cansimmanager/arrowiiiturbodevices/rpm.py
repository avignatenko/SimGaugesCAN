import logging

from .. import common
from ..can import Can
from ..devices import Device
from ..sim import Sim

logger = logging.getLogger(__name__)


class RPM(Device):

    CAN_ID = 21

    async def init(self):
        await self._sim.subscribe_dataref(
            "simcoders/rep/cockpit2/gauges/indicators/engine_0_rpm",
            None,
            self._on_rpm_update,
            5,
            freq=5,
        )

    async def _on_rpm_update(self, value):
        logger.debug("udpate received!! %s", value)
        await self._set_rpm(value)

    async def _set_rpm(self, value: float):
        await self._can.send(self.CAN_ID, 0, common.make_payload_float(value))
