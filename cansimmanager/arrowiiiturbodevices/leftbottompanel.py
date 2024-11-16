import logging
import asyncio

from .. import common
from ..devices import Device

logger = logging.getLogger(__name__)


class BusVolts:

    def __init__(self, sim):
        self._sim = sim
        self._volts = 0
        self._volts_ok = False
        self._callbacks = []

    async def init(self):
        await self._sim.subscribe_dataref(
            "sim/cockpit2/electrical/bus_volts",
            0,
            self._on_bus_volts,
            tolerance=0.1,
            freq=1,
        )

    async def _on_bus_volts(self, value):
        self._volts = value

        new_volts_ok = value > 5
        if self._volts_ok != new_volts_ok:
            self._volts_ok = new_volts_ok
            for callback in self._callbacks:
                asyncio.create_task(callback(new_volts_ok))

    def bus_volts_ok(self):
        return self._volts_ok

    def register_ok_status_change(self, callback):
        self._callbacks.append(callback)


class LeftBottomPanel(Device):

    CAN_ID = 23

    async def init(self):

        self._task_cranking = None
        self._bus_volts = BusVolts(self._sim)
        self._bus_volts.register_ok_status_change(self._bus_volts_ok_changed)
        self._gear_light_on = [False, False, False]

        await self._bus_volts.init()

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
            common.make_payload_byte(
                int(self._bus_volts.bus_volts_ok() and self._gear_light_on[0])
            ),
        )
        await self._can.send(
            self.CAN_ID,
            0,
            common.make_payload_byte(
                int(self._bus_volts.bus_volts_ok() and self._gear_light_on[1])
            ),
        )
        await self._can.send(
            self.CAN_ID,
            1,
            common.make_payload_byte(
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
                data = common.payload_float(payload)
                if data < 440:
                    roll_value = (data - 440) / (0 + 440) * 35
                else:
                    roll_value = (data - 440) / (1024 - 440) * 35

                await self._sim.send_dataref(
                    self._roll_knob_dataref_id, None, roll_value
                )

            case 6:  # ap left button
                data = common.payload_byte(payload)
                await self._sim.send_dataref(
                    self._thranda_autopilot_roll_dataref_id, None, data
                )

            case 7:  #  ap right button
                data = common.payload_byte(payload)
                await self._sim.send_dataref(
                    self._thranda_autopilot_hdg_dataref_id, None, data
                )

            case 9:  #  nav switch
                pass

            case 10:  # nav selector
                pass

            case 4:  # gear
                data = common.payload_byte(payload)
                await self._sim.send_dataref(
                    self._gear_handle_status_dataref_id, None, data
                )

            case 5:  # ignition
                data = common.payload_byte(payload)
                if data != 4:
                    if self._task_cranking is not None:
                        self._task_cranking.cancel()

                    await self._sim.send_dataref(self._ignition_key_dataref_id, 0, data)
                else:
                    self._task_cranking = asyncio.create_task(self.keep_cranking())

    async def keep_cranking(self):
        while True:
            await self._sim.send_dataref(self._ignition_key_dataref_id, 0, 4)
            await asyncio.sleep(0.05)
