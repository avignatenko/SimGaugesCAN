import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class GyroSuction2(cansimlib.Device2):
    def __init__(self, sim, can):
        super().__init__(sim, can, can_id=29)

    async def run(self):
        suction = await self.create_dataref_subscription("sim/cockpit2/gauges/indicators/suction_1_ratio")

        while True:
            value = await suction.receive_new_value()
            await self.can_send_float(0, value)
