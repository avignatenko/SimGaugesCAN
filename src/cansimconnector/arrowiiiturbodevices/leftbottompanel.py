import asyncio
import logging

from .. import cansimlib
from . import busvolts

logger = logging.getLogger(__name__)


class LeftBottomPanel(cansimlib.Device):

    CAN_ID = 23

    async def init(self):

        self._task_cranking = None
        self._bus_volts = busvolts.BusVolts(self._sim)
        self._bus_volts.register_ok_status_change(self._bus_volts_ok_changed)
        await self._bus_volts.init()

        self._gear_light_on = [False, False, False]

        self._roll_knob_dataref_id = await self._sim.get_dataref_id(
            "thranda/autopilot/rollKnob"
        )
        self._thranda_autopilot_roll_dataref_id = await self._sim.get_dataref_id(
            "thranda/autopilot/roll"
        )
        self._thranda_autopilot_hdg_dataref_id = await self._sim.get_dataref_id(
            "thranda/autopilot/hdg"
        )
        self._ignition_key_dataref_id = await self._sim.get_dataref_id(
            "sim/cockpit2/engine/actuators/ignition_key"
        )
        self._gear_handle_status_dataref_id = await self._sim.get_dataref_id(
            "sim/cockpit/switches/gear_handle_status"
        )

        await self._sim.subscribe_dataref(
            "sim/aircraft/parts/acf_gear_deploy",
            None,
            self._on_gear_deploy,
            tolerance=0.1,
            freq=2,
        )

        await self._can.subscribe_message(self.CAN_ID, self._on_can_event)

    async def _update_gear_leds(self):
        await self._can.send(
            self.CAN_ID,
            2,
            cansimlib.make_payload_byte(
                int(self._bus_volts.bus_volts_ok() and self._gear_light_on[0])
            ),
        )
        await self._can.send(
            self.CAN_ID,
            0,
            cansimlib.make_payload_byte(
                int(self._bus_volts.bus_volts_ok() and self._gear_light_on[1])
            ),
        )
        await self._can.send(
            self.CAN_ID,
            1,
            cansimlib.make_payload_byte(
                int(self._bus_volts.bus_volts_ok() and self._gear_light_on[2])
            ),
        )

    async def _bus_volts_ok_changed(self, value):
        await self._update_gear_leds()

    async def _on_gear_deploy(self, value):
        self._gear_light_on[0] = value[0] > 0.99
        self._gear_light_on[1] = value[1] > 0.99
        self._gear_light_on[2] = value[2] > 0.99
        await self._update_gear_leds()

    async def _on_can_event(self, port, payload):
        match port:
            case 8:  # ap rotator
                data = cansimlib.payload_float(payload)
                if data < 440:
                    roll_value = (data - 440) / (0 + 440) * 35
                else:
                    roll_value = (data - 440) / (1024 - 440) * 35

                await self._sim.send_dataref(
                    self._roll_knob_dataref_id, None, roll_value
                )

            case 6:  # ap left button
                data = cansimlib.payload_byte(payload)
                await self._sim.send_dataref(
                    self._thranda_autopilot_roll_dataref_id, None, data
                )

            case 7:  #  ap right button
                data = cansimlib.payload_byte(payload)
                await self._sim.send_dataref(
                    self._thranda_autopilot_hdg_dataref_id, None, data
                )

            case 9:  #  nav switch
                pass

            case 10:  # nav selector
                pass

            case 4:  # gear
                data = cansimlib.payload_byte(payload)
                await self._sim.send_dataref(
                    self._gear_handle_status_dataref_id, None, data
                )

            case 5:  # ignition
                data = cansimlib.payload_byte(payload)
                if self._task_cranking is not None:
                    self._task_cranking.cancel()
                    self._task_cranking = None

                if data != 4:
                    await self._sim.send_dataref(self._ignition_key_dataref_id, 0, data)
                else:
                    self._task_cranking = asyncio.create_task(self.keep_cranking())

    async def keep_cranking(self):
        while True:
            await self._sim.send_dataref(self._ignition_key_dataref_id, 0, 4)
            await asyncio.sleep(0.05)


class LeftBottomPane2(cansimlib.Device2):

    CAN_ID = 23

    def __init__(self, sim, can):
        super().__init__(sim, can)
        self._value_volts = None
        self._gear_light_on = [None] * 3
        self._keep_ingition_task = None

    async def _run_volts(self):
        volts = await self.create_dataref_subscription(
            "sim/cockpit2/electrical/bus_volts", index=[0], tolerance=0.1
        )
        while True:
            self._value_volts = await volts.receive_new_value()
            await self._update_gear_leds()

    async def _update_gear_leds(self):

        if None in [*self._gear_light_on, self._value_volts]:
            return

        await self._can.send(
            self.CAN_ID,
            2,
            cansimlib.make_payload_byte(
                int(busvolts.electrics_on(self._value_volts) and self._gear_light_on[0])
            ),
        )
        await self._can.send(
            self.CAN_ID,
            0,
            cansimlib.make_payload_byte(
                int(busvolts.electrics_on(self._value_volts) and self._gear_light_on[1])
            ),
        )
        await self._can.send(
            self.CAN_ID,
            1,
            cansimlib.make_payload_byte(
                int(busvolts.electrics_on(self._value_volts) and self._gear_light_on[2])
            ),
        )

    async def _run_gear_leds(self):

        gear_deploy_status = await self.create_dataref_subscription(
            "sim/aircraft/parts/acf_gear_deploy", index=[0, 1, 2], tolerance=0.1
        )

        while True:
            value = await gear_deploy_status.receive_new_value()
            self._gear_light_on[0] = value[0] > 0.99
            self._gear_light_on[1] = value[1] > 0.99
            self._gear_light_on[2] = value[2] > 0.99
            await self._update_gear_leds()

    async def _run_ap_rotator(self):
        dataref_id = await self._sim.get_dataref_id("thranda/autopilot/rollKnob")
        can_message = await self.create_can_message_subscription(
            self.CAN_ID, 8, cansimlib.CANMessageSubscription.CANType.FLOAT
        )

        while True:
            data = await can_message.receive_new_value()
            if data < 440:
                roll_value = (data - 440) / (0 + 440) * 35
            else:
                roll_value = (data - 440) / (1024 - 440) * 35

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
        dataref_id = await self._sim.get_dataref_id(
            "sim/cockpit/switches/gear_handle_status"
        )
        can_message = await self.create_can_message_subscription(
            self.CAN_ID, 4, cansimlib.CANMessageSubscription.CANType.BYTE
        )

        while True:
            data = await can_message.receive_new_value()
            await self._sim.send_dataref(dataref_id, None, data)

    async def _run_ignition(self):
        dataref_id = await self._sim.get_dataref_id(
            "sim/cockpit2/engine/actuators/ignition_key"
        )
        can_message = await self.create_can_message_subscription(
            self.CAN_ID, 5, cansimlib.CANMessageSubscription.CANType.BYTE
        )

        while True:
            data = await can_message.receive_new_value()
            if data != 4:
                if self._keep_ingition_task is not None:
                    self._keep_ingition_task.cancel()
                await self._sim.send_dataref(dataref_id, 0, data)
            else:
                self._keep_ingition_task = asyncio.create_task(
                    self._keep_ignition(dataref_id)
                )

    async def _keep_ignition(self, dataref_id):
        while True:
            await self._sim.send_dataref(dataref_id, 0, 4)
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
