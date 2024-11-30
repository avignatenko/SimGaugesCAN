import asyncio
import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class Altitude2(cansimlib.Device2):
    def __init__(self, sim, can):
        super().__init__(sim, can, can_id=17)

    async def run_knob(self):
        bar_in_hg_dataref_id = await self._sim.get_dataref_id(
            "sim/cockpit2/gauges/actuators/barometer_setting_in_hg_pilot"
        )

        knob = await self.create_can_message_subscription2(0, cansimlib.CANMessageSubscription.CANType.FLOAT)

        while True:
            value = await knob.receive_new_value()
            await self._sim.send_dataref(bar_in_hg_dataref_id, None, value)

    async def run_altitude(self):
        alt = await self.create_dataref_subscription(
            "simcoders/rep/cockpit2/gauges/indicators/altitude_ft_pilot", tolerance=0.1
        )

        while True:
            value = await alt.receive_new_value()
            await self.can_send_float(0, -value)

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.run_knob())
            tg.create_task(self.run_altitude())
