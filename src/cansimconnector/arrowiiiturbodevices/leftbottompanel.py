import asyncio
import logging

from cansimconnector import cansimlib
from cansimconnector.arrowiiiturbodevices import busvolts

logger = logging.getLogger(__name__)


class LeftBottomPane2(cansimlib.Device2):
    CAN_ID = 23
    IGNITION_ON_VALUE = 4

    def __init__(self, sim, can):
        super().__init__(sim, can)
        self._value_volts = None
        self._gear_light_on = [None] * 3
        self._keep_ingition_task = None
        super().enable_rate_limiter(1000)
        super().set_can_id(self.CAN_ID)

    async def _run_volts(self):
        volts = await self.create_dataref_subscription("sim/cockpit2/electrical/bus_volts", index=[0], tolerance=0.1)
        while True:
            self._value_volts = await volts.receive_new_value()
            await self._update_gear_leds()

    async def _update_gear_leds(self):
        if None in {*self._gear_light_on, self._value_volts}:
            return

        await self.can_send_byte(2, int(busvolts.electrics_on(self._value_volts) and self._gear_light_on[0]))
        await self.can_send_byte(0, int(busvolts.electrics_on(self._value_volts) and self._gear_light_on[1]))
        await self.can_send_byte(1, int(busvolts.electrics_on(self._value_volts) and self._gear_light_on[2]))

    async def _run_gear_leds(self):
        gear_deploy_status = await self.create_dataref_subscription(
            "sim/aircraft/parts/acf_gear_deploy", index=[0, 1, 2], tolerance=0.1
        )

        while True:
            value = await gear_deploy_status.receive_new_value()
            self._gear_light_on[0] = value[0] > 0.99  # noqa: PLR2004
            self._gear_light_on[1] = value[1] > 0.99  # noqa: PLR2004
            self._gear_light_on[2] = value[2] > 0.99  # noqa: PLR2004
            await self._update_gear_leds()

    async def _run_ap_rotator(self):
        dataref_id = await self._sim.get_dataref_id("thranda/autopilot/rollKnob")
        can_message = await self.create_can_message_subscription(
            self.CAN_ID, 8, cansimlib.CANMessageSubscription.CANType.FLOAT
        )

        while True:
            data = await can_message.receive_new_value()
            roll_value = (data - 440) / (0 + 440) * 35 if data < 440 else (data - 440) / (1024 - 440) * 35  # noqa:  PLR2004

            await self._sim.send_dataref(dataref_id, None, roll_value)

    async def _run_ap_left_button(self):
        dataref_id = await self._sim.get_dataref_id("thranda/autopilot/roll")
        can_message = await self.create_can_message_subscription(
            self.CAN_ID, 6, cansimlib.CANMessageSubscription.CANType.BYTE
        )

        while True:
            data = await can_message.receive_new_value()
            await self._sim.send_dataref(dataref_id, None, data)

    async def _run_ap_right_button(self):
        dataref_id = await self._sim.get_dataref_id("thranda/autopilot/hdg")
        can_message = await self.create_can_message_subscription(
            self.CAN_ID, 7, cansimlib.CANMessageSubscription.CANType.BYTE
        )

        while True:
            data = await can_message.receive_new_value()
            await self._sim.send_dataref(dataref_id, None, data)

    async def _run_gear_handle(self):
        dataref_id = await self._sim.get_dataref_id("sim/cockpit/switches/gear_handle_status")
        can_message = await self.create_can_message_subscription(
            self.CAN_ID, 4, cansimlib.CANMessageSubscription.CANType.BYTE
        )

        while True:
            data = await can_message.receive_new_value()
            await self._sim.send_dataref(dataref_id, None, data)

    async def _run_ignition(self):
        dataref_id = await self._sim.get_dataref_id("sim/cockpit2/engine/actuators/ignition_key")
        can_message = await self.create_can_message_subscription(
            self.CAN_ID, 5, cansimlib.CANMessageSubscription.CANType.BYTE
        )

        while True:
            data = await can_message.receive_new_value()
            if data != self.IGNITION_ON_VALUE:
                if self._keep_ingition_task is not None:
                    self._keep_ingition_task.cancel()
                await self._sim.send_dataref(dataref_id, 0, data)
            else:
                self._keep_ingition_task = asyncio.create_task(self._keep_ignition(dataref_id))

    async def _keep_ignition(self, dataref_id):
        while True:
            await self._sim.send_dataref(dataref_id, 0, self.IGNITION_ON_VALUE)
            await asyncio.sleep(0.05)

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._run_volts())
            tg.create_task(self._run_ap_rotator())
            tg.create_task(self._run_gear_leds())
            tg.create_task(self._run_ap_left_button())
            tg.create_task(self._run_ap_right_button())
            tg.create_task(self._run_gear_handle())
            tg.create_task(self._run_ignition())
