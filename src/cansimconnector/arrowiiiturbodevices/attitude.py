import asyncio
import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class Attitude2(cansimlib.Device2):
    CAN_ID = 28

    async def run_pitch(self):
        pitch = await self.create_dataref_subscription(
            "simcoders/rep/cockpit2/gauges/indicators/attitude_indicator_0_pitch",
            tolerance=0.05,
        )

        while True:
            value = await pitch.receive_new_value()
            await self._can.send(self.CAN_ID, 0, cansimlib.make_payload_float(value))

    async def run_roll(self):
        roll = await self.create_dataref_subscription(
            "simcoders/rep/cockpit2/gauges/indicators/attitude_indicator_0_roll",
            tolerance=0.05,
        )

        while True:
            value = await roll.receive_new_value()
            await self._can.send(self.CAN_ID, 1, cansimlib.make_payload_float(value))

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.run_pitch())
            tg.create_task(self.run_roll())
