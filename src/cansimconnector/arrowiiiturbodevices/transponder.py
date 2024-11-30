import asyncio
import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class Transponder2(cansimlib.Device2):
    LED_VALUE_ON = 0.3

    def __init__(self, sim, can):
        super().__init__(sim, can, can_id=31)

    async def run_volts(self):
        volts = await self.create_dataref_subscription("sim/cockpit2/electrical/bus_volts", index=[0], tolerance=0.1)
        while True:
            value = await volts.receive_new_value()
            await self.can_send_byte(1, int(value))

    async def run_transponder_code(self):
        code_dataref_id = await self._sim.get_dataref_id("sim/cockpit2/radios/actuators/transponder_code")
        code_message = await self.create_can_message_subscription2(1, cansimlib.CANMessageSubscription.CANType.USHORT)

        while True:
            squawk = await code_message.receive_new_value()
            await self._sim.send_dataref(code_dataref_id, None, squawk)

    async def run_transponder_mode(self):
        mode_dataref_id = await self._sim.get_dataref_id("sim/cockpit2/radios/actuators/transponder_mode")
        mode_message = await self.create_can_message_subscription2(0, cansimlib.CANMessageSubscription.CANType.BYTE)

        while True:
            mode = await mode_message.receive_new_value()
            await self._sim.send_dataref(mode_dataref_id, None, mode - 1)

    async def run_transponder_ident(self):
        ident_message = await self.create_can_message_subscription2(2, cansimlib.CANMessageSubscription.CANType.BYTE)

        while True:
            await ident_message.receive_new_value()

    async def run_transponder_brightness(self):
        brightness = await self.create_dataref_subscription(
            "sim/cockpit2/radios/indicators/transponder_brightness", tolerance=0.1
        )

        while True:
            value = await brightness.receive_new_value()
            await self.can_send_byte(2, 1 if value > self.LED_VALUE_ON else 0)

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.run_volts())
            tg.create_task(self.run_transponder_code())
            tg.create_task(self.run_transponder_mode())
            tg.create_task(self.run_transponder_ident())
            tg.create_task(self.run_transponder_brightness())
