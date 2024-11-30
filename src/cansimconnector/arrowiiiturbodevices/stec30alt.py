import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class STec30Alt2(cansimlib.Device2):
    CAN_ID = 32

    async def run(self):
        self._on = False
        can_message = await self.create_can_message_subscription(
            self.CAN_ID,
            0,
            cansimlib.CANMessageSubscription.CANType.BYTE,
            compare=cansimlib.CANMessageSubscription.ValuePolicy.SEND_ALWAYS,
        )

        while True:
            await can_message.receive_new_value()
            # test actions
            self._on = not self._on
            await self._can.send_byte(self.CAN_ID, 0, int(self._on))
            await self._can.send_byte(self.CAN_ID, 1, int(self._on))
