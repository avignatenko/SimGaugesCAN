import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class GyroSuction2(cansimlib.Device2):
    CAN_ID = 29

    async def run(self):
        suction = await self.create_dataref_subscription("sim/cockpit2/gauges/indicators/suction_1_ratio")

        while True:
            value = await suction.receive_new_value()
            await self._can.send_float(self.CAN_ID, 0, value)
