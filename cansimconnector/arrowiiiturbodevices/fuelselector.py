import logging

from .. import cansimlib

logger = logging.getLogger(__name__)


class FuelSelector(cansimlib.Device):

    CAN_ID = 30

    async def init(self):

        self._fuel_tank_selector_dataref_id = await self._sim.get_dataref_id(
            "sim/cockpit2/fuel/fuel_tank_selector"
        )

        await self._can.subscribe_message(self.CAN_ID, self._on_fuel_tank_selector)

    async def _on_fuel_tank_selector(self, port, payload):
        value = cansimlib.payload_byte(payload)

        selector_map = {1: 1, 2: 3, 0: 0}
        xpl_selector = selector_map[value]

        await self._sim.send_dataref(
            self._fuel_tank_selector_dataref_id, None, xpl_selector
        )
