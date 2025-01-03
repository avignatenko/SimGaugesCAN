import asyncio
import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class MPR2(cansimlib.Device):
    def __init__(self, sim, can):
        super().__init__(sim, can, can_id=22)

    async def run_fuel_flow(self):
        fuel_flow = await self.create_dataref_subscription("simcoders/rep/indicators/fuel/fuel_flow_0")

        while True:
            value = await fuel_flow.receive_new_value()
            await self.can_send_float(1, value * 1350)

    async def run_mpr(self):
        mpr = await self.create_dataref_subscription("sim/cockpit2/engine/indicators/MPR_in_hg", index=[0])

        while True:
            value = await mpr.receive_new_value()
            await self.can_send_float(0, value)

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.run_fuel_flow())
            tg.create_task(self.run_mpr())
