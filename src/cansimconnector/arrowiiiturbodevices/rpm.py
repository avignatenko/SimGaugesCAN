import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class RPM2(cansimlib.Device2):
    CAN_ID = 21

    async def run(self):
        rpm = await self.create_dataref_subscription(
            "simcoders/rep/cockpit2/gauges/indicators/engine_0_rpm", tolerance=5
        )

        while True:
            value = await rpm.receive_new_value()
            await self._can.send(self.CAN_ID, 0, cansimlib.make_payload_float(value))
