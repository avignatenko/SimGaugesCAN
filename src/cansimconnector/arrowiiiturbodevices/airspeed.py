import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class Airspeed2(cansimlib.Device):
    def __init__(self, sim, can):
        super().__init__(sim, can, can_id=16)

    async def run(self):
        airspeed = await self.create_dataref_subscription("simcoders/rep/cockpit2/gauges/indicators/airspeed_kts_pilot")

        while True:
            value = await airspeed.receive_new_value()
            await self.can_send_float(0, value)
