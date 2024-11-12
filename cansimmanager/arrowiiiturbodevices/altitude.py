import logging

from .. import common
from ..devices import Device

logger = logging.getLogger(__name__)


class Altitude(Device):

    CAN_ID = 17

    async def init(self):
        await self._sim.subscribe_dataref(
            "simcoders/rep/cockpit2/gauges/indicators/altitude_ft_pilot",
            self._on_altitude_update,
            tolerance=0.25,
            freq=5
        )

        self._bar_in_hg_dataref_id = await self._sim.get_dataref_id(
            "sim/cockpit2/gauges/actuators/barometer_setting_in_hg_pilot"
        )

        await self._can.subscribe_message(self.CAN_ID, self._on_pressure_knob_rotated)

    async def _on_altitude_update(self, value):
        logging.debug("udpate received!! %s", value)
        await self._set_altitude(value)

    async def _set_altitude(self, value: float):
        await self._can.send(self.CAN_ID, 0, common.make_payload_float(-value))

    async def _on_pressure_knob_rotated(self, port, payload):
        value = common.payload_float(payload)
        await self._sim.send_dataref(self._bar_in_hg_dataref_id, value)
