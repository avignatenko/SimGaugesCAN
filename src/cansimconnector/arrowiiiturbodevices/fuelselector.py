import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class FuelSelector2(cansimlib.Device):
    def __init__(self, sim, can):
        super().__init__(sim, can, can_id=30)

    async def run(self):
        fuel_tank_selector_dataref_id = await self._sim.get_dataref_id("sim/cockpit2/fuel/fuel_tank_selector")

        tank_selector_knob = await self.create_can_message_subscription2(
            0, cansimlib.CANMessageSubscription.CANType.BYTE
        )

        while True:
            value = await tank_selector_knob.receive_new_value()

            selector_map = {1: 1, 2: 3, 0: 0}
            xpl_selector = selector_map[value]

            await self._sim.send_dataref(fuel_tank_selector_dataref_id, xpl_selector)
