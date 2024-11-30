import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class VerticalSpeed2(cansimlib.Device2):
    def __init__(self, sim, can):
        super().__init__(sim, can, can_id=18)

    async def run(self):
        vspeed = await self.create_dataref_subscription("simcoders/rep/cockpit2/gauges/indicators/vvi_fpm_pilot")

        while True:
            value = await vspeed.receive_new_value()
            await self.can_send_float(0, value / 100)
