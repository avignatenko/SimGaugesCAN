import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class VerticalSpeed(cansimlib.Device):

    CAN_ID = 18

    async def init(self):
        await self._sim.subscribe_dataref(
            "simcoders/rep/cockpit2/gauges/indicators/vvi_fpm_pilot",
            None,
            self._on_vertspeed_update,
            0.01,
        )

    async def _on_vertspeed_update(self, value):
        logger.debug("update received!! %s", value)
        await self._set_vertspeed(value)

    async def _set_vertspeed(self, value: float):
        await self._can.send(self.CAN_ID, 0, cansimlib.make_payload_float(value / 100))


class VerticalSpeed2(cansimlib.Device2):

    CAN_ID = 18

    async def run(self):
        vspeed = await self.create_dataref_subscription(
            "simcoders/rep/cockpit2/gauges/indicators/vvi_fpm_pilot"
        )

        while True:
            value = await vspeed.receive_new_value()
            await self._can.send(
                self.CAN_ID, 0, cansimlib.make_payload_float(value / 100)
            )
