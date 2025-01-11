import logging
import asyncio

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class STec30Alt2(cansimlib.Device):
    def __init__(self, sim, can):
        super().__init__(sim, can, can_id=32)

    async def _run_can(self):
        # custom dataref. 0 - off, 1 - on
        ap_on_dataref_id = await self._sim.get_dataref_id("ai/cockpit/gauges/ap/engaged")

        can_message = await self.create_can_message_subscription2(
            0,
            cansimlib.CANMessageSubscription.CANType.BYTE,
            compare=cansimlib.CANMessageSubscription.ValuePolicy.SEND_ALWAYS,
        )

        while True:
            await can_message.receive_new_value()

            self._on = not self._on
            await self.can_send_byte(0, int(self._on))
            await self.can_send_byte(1, int(self._on))

            await self._sim.send_dataref(ap_on_dataref_id, self._on)

    async def _run_sim(self):
        # custom dataref. 0 - no warning, 1 - pitch up, 2 - pitch down
        pitch_trim_warning = await self.create_dataref_subscription("ai/cockpit/gauges/ap/pitch_trim_warning")

        while True:
            value = await pitch_trim_warning.receive_new_value()
            match value:
                case 0:
                    await self.can_send_byte(2, 0)
                    await self.can_send_byte(3, 0)
                case 1:
                    await self.can_send_byte(2, 1)
                    await self.can_send_byte(3, 0)
                case 2:
                    await self.can_send_byte(2, 0)
                    await self.can_send_byte(3, 1)
                case _:
                    logger.warning("Received invalid pitch trim warning value")

    async def run(self):
        self._on = False

        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._run_can())
            tg.create_task(self._run_sim())
