import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class STec30Alt2(cansimlib.Device2):
    def __init__(self, sim, can):
        super().__init__(sim, can, can_id=32)

    async def run(self):
        self._on = False
        can_message = await self.create_can_message_subscription2(
            0,
            cansimlib.CANMessageSubscription.CANType.BYTE,
            compare=cansimlib.CANMessageSubscription.ValuePolicy.SEND_ALWAYS,
        )

        while True:
            await can_message.receive_new_value()
            # test actions
            self._on = not self._on
            await self.can_send_byte(0, int(self._on))
            await self.can_send_byte(1, int(self._on))
