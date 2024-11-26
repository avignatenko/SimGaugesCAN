import asyncio
import logging

from .. import cansimlib

logger = logging.getLogger(__name__)


class IndicatorsPanel1(cansimlib.Device):
    def __init__(self, sim: cansimlib.XPlaneClient, can: cansimlib.CANClient):
        super().__init__(sim, can)

        generator = cansimlib.SingleValueIndicator(
            sim,
            can,
            can_id=27,
            port=0,
            datarefs=[
                cansimlib.SingleValueIndicator.DatarefSubsription(
                    dataref_str="sim/cockpit2/electrical/generator_amps",
                    idx=0,
                    tolerance=0.1,
                )
            ],
        )

        oil_temp = cansimlib.SingleValueIndicator(
            sim,
            can,
            can_id=27,
            port=1,
            datarefs=[
                cansimlib.SingleValueIndicator.DatarefSubsription(
                    dataref_str="simcoders/rep/engine/oil/temp_f_0",
                    tolerance=0.1,
                )
            ],
        )

        oil_pressure = cansimlib.SingleValueIndicator(
            sim,
            can,
            can_id=27,
            port=2,
            datarefs=[
                cansimlib.SingleValueIndicator.DatarefSubsription(
                    dataref_str="simcoders/rep/engine/oil/press_psi_0",
                    tolerance=0.1,
                )
            ],
        )

        outside_air = cansimlib.SingleValueIndicator(
            sim,
            can,
            can_id=27,
            port=3,
            datarefs=[
                cansimlib.SingleValueIndicator.DatarefSubsription(
                    dataref_str="sim/cockpit2/temperature/outside_air_temp_degc",
                    tolerance=0.5,
                )
            ],
        )

        self._devices = [generator, oil_temp, oil_pressure, outside_air]

    async def init(self):
        asyncio.gather(*map(lambda obj: obj.init(), self._devices))


class IndicatorsPanel1_2(cansimlib.Device2):

    CAN_ID = 27

    async def run_indicator(self, dataref_str, port, idx=None, tolerance=0.01):
        dataref = await self.create_dataref_subscription(
            dataref_str, index=idx, tolerance=tolerance
        )

        while True:
            value = await dataref.receive_new_value()
            await self._can.send(self.CAN_ID, port, cansimlib.make_payload_float(value))

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
