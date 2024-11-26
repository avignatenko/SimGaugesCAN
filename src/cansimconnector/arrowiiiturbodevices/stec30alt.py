import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class STec30Alt(cansimlib.Device):

    CAN_ID = 32

    async def init(self):
        self._on = False
        await self._can.subscribe_message(self.CAN_ID, self._on_button_pressed)

    async def _on_button_pressed(self, port, payload):
        # test actions
        self._on = not self._on
        await self._can.send(self.CAN_ID, 0, cansimlib.make_payload_byte(int(self._on)))
        await self._can.send(self.CAN_ID, 1, cansimlib.make_payload_byte(int(self._on)))


class STec30Alt2(cansimlib.Device2):

    CAN_ID = 32

    async def run(self):
        self._on = False
        can_message = await self.create_can_message_subscription(
            self.CAN_ID, 0, cansimlib.CANMessageSubscription.CANType.BYTE, compare=False
        )

        while True:
            await can_message.receive_new_value()
            # test actions
            self._on = not self._on
            await self._can.send(
                self.CAN_ID, 0, cansimlib.make_payload_byte(int(self._on))
            )
            await self._can.send(
                self.CAN_ID, 1, cansimlib.make_payload_byte(int(self._on))
            )
