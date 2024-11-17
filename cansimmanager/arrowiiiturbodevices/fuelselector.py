import logging

from .. import common
from ..devices import Device

logger = logging.getLogger(__name__)


class FuelSelector(Device):

    CAN_ID = 30

    async def init(self):

        self._fuel_tank_selector_dataref_id = await self._sim.get_dataref_id(
            "sim/cockpit2/fuel/fuel_tank_selector"
        )

        await self._can.subscribe_message(self.CAN_ID, self._on_fuel_tank_selector)

    async def _on_fuel_tank_selector(self, port, payload):
        value = common.payload_byte(payload)

        xpl_selector = 0
        if payload == 1:
            xpl_selector = 1
        elif payload == 2:
            xpl_selector = 3

        await self._sim.send_dataref(
            self._fuel_tank_selector_dataref_id, None, xpl_selector
        )
