import asyncio
import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class TurnRoll2(cansimlib.Device2):
    def __init__(self, sim, can):
        super().__init__(sim, can, can_id=19)

    async def run_slip(self):
        slip = await self.create_dataref_subscription("sim/cockpit2/gauges/indicators/slip_deg")

        while True:
            value = await slip.receive_new_value()
            await self.can_send_float(1, -value * 3)

    async def run_roll(self):
        roll = await self.create_dataref_subscription(
            "sim/cockpit2/gauges/indicators/turn_rate_roll_deg_pilot", tolerance=0.1
        )

        while True:
            value = await roll.receive_new_value()
            await self.can_send_float(0, value)

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.run_slip())
            tg.create_task(self.run_roll())
