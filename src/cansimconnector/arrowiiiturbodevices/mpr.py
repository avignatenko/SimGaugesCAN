import asyncio
import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class MPR(cansimlib.Device):

    CAN_ID = 22

    async def init(self):
        await self._sim.subscribe_dataref(
            "sim/cockpit2/engine/indicators/MPR_in_hg",
            None,
            self._on_mpr_update,
            0.01,
            freq=5,
        )

        await self._sim.subscribe_dataref(
            "simcoders/rep/indicators/fuel/fuel_flow_0",
            None,
            self._on_fuel_flow_update,
            0.01,
            freq=5,
        )

    async def _on_mpr_update(self, value):
        logger.debug("udpate received!! %s", value)
        await self._set_mpr(value[0])

    async def _set_mpr(self, value: float):
        await self._can.send(self.CAN_ID, 0, cansimlib.make_payload_float(value))

    async def _on_fuel_flow_update(self, value):
        logger.debug("udpate received!! %s", value)
        await self._set_fuel_flow(value)

    async def _set_fuel_flow(self, value: float):
        await self._can.send(self.CAN_ID, 1, cansimlib.make_payload_float(value * 1350))


class MPR2(cansimlib.Device2):

    CAN_ID = 22

    async def run_fuel_flow(self):
        fuel_flow = await self.create_dataref_subscription(
            "simcoders/rep/indicators/fuel/fuel_flow_0"
        )

        while True:
            value = await fuel_flow.receive_new_value()
            await self._can.send(
                self.CAN_ID, 1, cansimlib.make_payload_float(value * 1350)
            )

    async def run_mpr(self):
        mpr = await self.create_dataref_subscription(
            "sim/cockpit2/engine/indicators/MPR_in_hg", index=[0]
        )

        while True:
            value = await mpr.receive_new_value()
            await self._can.send(self.CAN_ID, 0, cansimlib.make_payload_float(value))

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.run_fuel_flow())
            tg.create_task(self.run_mpr())
