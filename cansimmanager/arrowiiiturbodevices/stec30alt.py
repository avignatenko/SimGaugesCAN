import logging

from .. import common
from ..devices import Device

logger = logging.getLogger(__name__)

    
class STec30Alt(Device):

    CAN_ID = 32
  
    async def init(self):
        self._on = False
        await self._can.subscribe_message(self.CAN_ID, self._on_button_pressed)

    async def _on_button_pressed(self, port, payload):
        # test actions
        self._on = not self._on
        await self._can.send(self.CAN_ID, 0, common.make_payload_byte(int(self._on)))
        await self._can.send(self.CAN_ID, 1, common.make_payload_byte(int(self._on)))