import asyncio
import logging

from .. import cansimlib

logger = logging.getLogger(__name__)


class Altitude(cansimlib.Device):

    CAN_ID = 17

    async def init(self):
        await self._sim.subscribe_dataref(
            "simcoders/rep/cockpit2/gauges/indicators/altitude_ft_pilot",
            None,
            self._on_altitude_update,
            tolerance=0.1,
            freq=5,
        )

        self._bar_in_hg_dataref_id = await self._sim.get_dataref_id(
            "sim/cockpit2/gauges/actuators/barometer_setting_in_hg_pilot"
        )

        await self._can.subscribe_message(self.CAN_ID, self._on_pressure_knob_rotated)

    async def _on_altitude_update(self, value):
        logger.debug("udpate received!! %s", value)
        await self._set_altitude(value)

    async def _set_altitude(self, value: float):
        await self._can.send(self.CAN_ID, 0, cansimlib.make_payload_float(-value))

    async def _on_pressure_knob_rotated(self, port, payload):
        value = cansimlib.payload_float(payload)
        await self._sim.send_dataref(self._bar_in_hg_dataref_id, None, value)


class Altitude2(cansimlib.Device2):

    CAN_ID = 17

    async def run_knob(self):

        bar_in_hg_dataref_id = await self._sim.get_dataref_id(
            "sim/cockpit2/gauges/actuators/barometer_setting_in_hg_pilot"
        )

        knob = await cansimlib.CANMessageSubscription.create(
            self._can, self.CAN_ID, 0, cansimlib.CANMessageSubscription.CANType.FLOAT
        )

        while True:
            value = await knob.receive_new_value()
            await self._sim.send_dataref(bar_in_hg_dataref_id, None, value)

    async def run_altitude(self):
        alt = await self.create_dataref_subscription(
            "simcoders/rep/cockpit2/gauges/indicators/altitude_ft_pilot", tolerance=0.1
        )

        while True:
            value = await alt.receive_new_value()
            await self._can.send(self.CAN_ID, 0, cansimlib.make_payload_float(-value))

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.run_knob())
            tg.create_task(self.run_altitude())
