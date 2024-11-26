import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class RPM(cansimlib.Device):

    CAN_ID = 21

    async def init(self):
        await self._sim.subscribe_dataref(
            "simcoders/rep/cockpit2/gauges/indicators/engine_0_rpm",
            None,
            self._on_rpm_update,
            5,
            freq=5,
        )

    async def _on_rpm_update(self, value):
        logger.debug("udpate received!! %s", value)
        await self._set_rpm(value)

    async def _set_rpm(self, value: float):
        await self._can.send(self.CAN_ID, 0, cansimlib.make_payload_float(value))


class RPM2(cansimlib.Device2):

    CAN_ID = 21

    async def run(self):
        rpm = await self.create_dataref_subscription(
            "simcoders/rep/cockpit2/gauges/indicators/engine_0_rpm", tolerance=5
        )

        while True:
            value = await rpm.receive_new_value()
            await self._can.send(self.CAN_ID, 0, cansimlib.make_payload_float(value))
