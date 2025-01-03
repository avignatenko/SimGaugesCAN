import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class RPM2(cansimlib.Device):
    def __init__(self, sim, can):
        super().__init__(sim, can, can_id=21)

    async def run(self):
        rpm = await self.create_dataref_subscription(
            "simcoders/rep/cockpit2/gauges/indicators/engine_0_rpm", tolerance=5
        )

        while True:
            value = await rpm.receive_new_value()
            await self.can_send_float(0, value)
