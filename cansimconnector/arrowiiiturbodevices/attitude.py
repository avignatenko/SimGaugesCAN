import asyncio
import logging

from .. import cansimlib

logger = logging.getLogger(__name__)


class Attitude(cansimlib.Device):

    CAN_ID = 28

    async def init(self):
        await self._sim.subscribe_dataref(
            "simcoders/rep/cockpit2/gauges/indicators/attitude_indicator_0_roll",
            None,
            self._on_roll_update,
            0.05,
        )

        await self._sim.subscribe_dataref(
            "simcoders/rep/cockpit2/gauges/indicators/attitude_indicator_0_pitch",
            None,
            self._on_pitch_update,
            0.05,
        )

    async def _on_roll_update(self, value):
        logger.debug("udpate received!! %s", value)
        await self._set_roll(value)

    async def _set_roll(self, value: float):
        await self._can.send(self.CAN_ID, 1, cansimlib.make_payload_float(value))

    async def _on_pitch_update(self, value):
        logger.debug("udpate received!! %s", value)
        await self._set_pitch(value)

    async def _set_pitch(self, value: float):
        await self._can.send(self.CAN_ID, 0, cansimlib.make_payload_float(value))


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
