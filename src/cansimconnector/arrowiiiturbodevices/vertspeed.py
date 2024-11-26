import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class VerticalSpeed2(cansimlib.Device2):
    CAN_ID = 18

    async def run(self):
        vspeed = await self.create_dataref_subscription("simcoders/rep/cockpit2/gauges/indicators/vvi_fpm_pilot")

        while True:
            value = await vspeed.receive_new_value()
            await self._can.send(self.CAN_ID, 0, cansimlib.make_payload_float(value / 100))
