import asyncio
import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class IndicatorsPanel(cansimlib.Device2):
    CAN_ID = 27

    async def run_indicator(self, dataref_str, port, idx=None, tolerance=0.01):
        dataref = await self.create_dataref_subscription(dataref_str, index=idx, tolerance=tolerance)

        while True:
            value = await dataref.receive_new_value()
            await self._can.send_float(self.CAN_ID, port, value)

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(
                self.run_indicator(
                    "sim/cockpit2/electrical/generator_amps",
                    port=0,
                    idx=[0],
                    tolerance=0.1,
                )
            )

            tg.create_task(
                self.run_indicator(
                    "simcoders/rep/engine/oil/temp_f_0",
                    port=1,
                    tolerance=0.1,
                )
            )

            tg.create_task(
                self.run_indicator(
                    "simcoders/rep/engine/oil/press_psi_0",
                    port=2,
                    tolerance=0.1,
                )
            )

            tg.create_task(
                self.run_indicator(
                    "sim/cockpit2/temperature/outside_air_temp_degc",
                    port=3,
                    tolerance=0.4,
                )
            )
