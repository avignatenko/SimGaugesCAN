import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class Airspeed2(cansimlib.Device2):
    CAN_ID = 16

    async def run(self):
        airspeed = await self.create_dataref_subscription("simcoders/rep/cockpit2/gauges/indicators/airspeed_kts_pilot")

        while True:
            value = await airspeed.receive_new_value()
            await self._can.send_float(self.CAN_ID, 0, value)
