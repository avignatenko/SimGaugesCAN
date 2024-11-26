import asyncio
import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class IndicatorsPanel2_2(cansimlib.Device2):
    CAN_ID = 25

    async def run_indicator(self, dataref_str, port, idx=None, tolerance=0.01):
        dataref = await self.create_dataref_subscription(dataref_str, index=idx, tolerance=tolerance)

        while True:
            value = await dataref.receive_new_value()
            await self._can.send(self.CAN_ID, port, cansimlib.make_payload_float(value))

    async def run_indicator_fuel(self, dataref_str, port, idx=None, tolerance=0.01):
        dataref = await self.create_dataref_subscription(dataref_str, index=idx, tolerance=tolerance)

        while True:
            value = await dataref.receive_new_value()
            await self._can.send(self.CAN_ID, port, cansimlib.make_payload_float(value * 40))

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.run_indicator_fuel("simcoders/rep/indicators/fuel/fuel_quantity_ratio_0", port=2))

            tg.create_task(self.run_indicator_fuel("simcoders/rep/indicators/fuel/fuel_quantity_ratio_1", port=0))

            tg.create_task(
                self.run_indicator(
                    "simcoders/rep/cockpit2/gauges/indicators/fuel_press_psi_0",
                    port=1,
                    tolerance=0.1,
                )
            )
