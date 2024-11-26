import asyncio
import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class TurnRoll(cansimlib.Device):

    CAN_ID = 19

    async def init(self):
        await self._sim.subscribe_dataref(
            "sim/cockpit2/gauges/indicators/slip_deg",
            None,
            self._on_slip_deg_update,
            0.01,
        )

        await self._sim.subscribe_dataref(
            "sim/cockpit2/gauges/indicators/turn_rate_roll_deg_pilot",
            None,
            self._on_turn_rate_update,
            0.1,
        )

    async def _on_slip_deg_update(self, value):
        logger.debug("udpate received!! %s", value)
        await self._set_slip_deg(value)

    async def _set_slip_deg(self, value: float):
        await self._can.send(self.CAN_ID, 1, cansimlib.make_payload_float(-value * 3))

    async def _on_turn_rate_update(self, value):
        logger.debug("udpate received!! %s", value)
        await self._set_turn_rate(value)

    async def _set_turn_rate(self, value: float):
        await self._can.send(self.CAN_ID, 0, cansimlib.make_payload_float(value))


class TurnRoll2(cansimlib.Device2):

    CAN_ID = 19

    async def run_slip(self):
        slip = await self.create_dataref_subscription(
            "sim/cockpit2/gauges/indicators/slip_deg"
        )

        while True:
            value = await slip.receive_new_value()
            await self._can.send(
                self.CAN_ID, 1, cansimlib.make_payload_float(-value * 3)
            )

    async def run_roll(self):
        roll = await self.create_dataref_subscription(
            "sim/cockpit2/gauges/indicators/turn_rate_roll_deg_pilot", tolerance=0.1
        )

        while True:
            value = await roll.receive_new_value()
            await self._can.send(self.CAN_ID, 0, cansimlib.make_payload_float(value))

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.run_slip())
            tg.create_task(self.run_roll())
