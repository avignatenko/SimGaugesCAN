import asyncio
import logging

from .. import cansimlib

logger = logging.getLogger(__name__)


class IndicatorsPanel2(cansimlib.Device):
    def __init__(self, sim: cansimlib.XPlaneClient, can: cansimlib.CANClient):
        super().__init__(sim, can)

        fuel_quantity_0 = cansimlib.SingleValueIndicator(
            sim,
            can,
            can_id=25,
            port=2,
            datarefs=[
                cansimlib.SingleValueIndicator.DatarefSubsription(
                    dataref_str="simcoders/rep/indicators/fuel/fuel_quantity_ratio_0",
                    idx=None,
                    tolerance=0.1,
                )
            ],
            dataref_to_value=lambda dataref: dataref * 40,
        )

        fuel_quantity_1 = cansimlib.SingleValueIndicator(
            sim,
            can,
            can_id=25,
            port=0,
            datarefs=[
                cansimlib.SingleValueIndicator.DatarefSubsription(
                    dataref_str="simcoders/rep/indicators/fuel/fuel_quantity_ratio_1",
                    idx=None,
                    tolerance=0.1,
                )
            ],
            dataref_to_value=lambda dataref: dataref * 40,
        )

        fuel_press = cansimlib.SingleValueIndicator(
            sim,
            can,
            can_id=25,
            port=1,
            datarefs=[
                cansimlib.SingleValueIndicator.DatarefSubsription(
                    dataref_str="simcoders/rep/cockpit2/gauges/indicators/fuel_press_psi_0",
                    idx=None,
                    tolerance=0.1,
                )
            ],
        )

        self._devices = [fuel_quantity_0, fuel_quantity_1, fuel_press]

    async def init(self):
        asyncio.gather(*map(lambda obj: obj.init(), self._devices))


class IndicatorsPanel2_2(cansimlib.Device2):

    CAN_ID = 25

    async def run_indicator(self, dataref_str, port, idx=None, tolerance=0.01):
        value = await self.create_dataref_subscription(
            dataref_str, index=idx, tolerance=tolerance
        )

        while True:
            value = await value.receive_new_value()
            await self._can.send(self.CAN_ID, port, cansimlib.make_payload_float(value))

    async def run_indicator_fuel(self, dataref_str, port, idx=None, tolerance=0.01):
        value = await self.create_dataref_subscription(
            dataref_str, index=idx, tolerance=tolerance
        )

        while True:
            value = await value.receive_new_value()
            await self._can.send(
                self.CAN_ID, port, cansimlib.make_payload_float(value * 40)
            )

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(
                self.run_indicator_fuel(
                    "simcoders/rep/indicators/fuel/fuel_quantity_ratio_0",
                    port=2,
                    tolerance=0.1,
                )
            )

            tg.create_task(
                self.run_indicator_fuel(
                    "simcoders/rep/indicators/fuel/fuel_quantity_ratio_1",
                    port=0,
                    tolerance=0.1,
                )
            )

            tg.create_task(
                self.run_indicator(
                    "simcoders/rep/cockpit2/gauges/indicators/fuel_press_psi_0",
                    port=1,
                    tolerance=0.1,
                )
            )
