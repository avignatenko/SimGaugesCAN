import asyncio
import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class ButtonsPanel(cansimlib.Device):

    CAN_ID = 24

    def __init__(self, sim: cansimlib.XPlaneClient, can: cansimlib.CANClient):
        super().__init__(sim, can)

        self._devices = [
            cansimlib.PhysicalSwitch(
                sim,
                can,
                can_id=self.CAN_ID,
                port=7,
                dataref_str="sim/cockpit/electrical/battery_on",
                idx=None,
                payload_to_dataref=lambda payload: cansimlib.payload_byte(payload),
            ),
            cansimlib.PhysicalSwitch(
                sim,
                can,
                can_id=self.CAN_ID,
                port=6,
                dataref_str="sim/cockpit/electrical/generator_on",
                idx=0,
                payload_to_dataref=lambda payload: cansimlib.payload_byte(payload),
            ),
            cansimlib.PhysicalSwitch(
                sim,
                can,
                can_id=self.CAN_ID,
                port=5,
                dataref_str="simcoders/rep/cockpit2/engine/actuators/fuel_pump_0",
                idx=None,
                payload_to_dataref=lambda payload: cansimlib.payload_byte(payload),
            ),
            cansimlib.PhysicalSwitch(
                sim,
                can,
                can_id=self.CAN_ID,
                port=4,
                dataref_str="sim/cockpit/electrical/landing_lights_on",
                idx=None,
                payload_to_dataref=lambda payload: cansimlib.payload_byte(payload),
            ),
            cansimlib.PhysicalSwitch(
                sim,
                can,
                can_id=self.CAN_ID,
                port=2,
                dataref_str="sim/cockpit/electrical/beacon_lights_on",
                idx=None,
                payload_to_dataref=lambda payload: cansimlib.payload_byte(payload),
            ),
            cansimlib.PhysicalSwitch(
                sim,
                can,
                can_id=self.CAN_ID,
                port=1,
                dataref_str="sim/cockpit/electrical/strobe_lights_on",
                idx=None,
                payload_to_dataref=lambda payload: cansimlib.payload_byte(payload),
            ),
            cansimlib.PhysicalSwitch(
                sim,
                can,
                can_id=self.CAN_ID,
                port=0,
                dataref_str="sim/cockpit/switches/pitot_heat_on",
                idx=None,
                payload_to_dataref=lambda payload: cansimlib.payload_byte(payload),
            ),
        ]

    async def init(self):
        asyncio.gather(*(obj.init() for obj in self._devices))


class ButtonsPanel2(cansimlib.Device2):

    CAN_ID = 24

    async def run_button(self, dataref_str, port, idx=None):
        dataref_id = await self._sim.get_dataref_id(dataref_str)
        can_message = await self.create_can_message_subscription(
            self.CAN_ID, port, cansimlib.CANMessageSubscription.CANType.BYTE
        )

        while True:
            value = await can_message.receive_new_value()
            await self._sim.send_dataref(dataref_id, idx, value)

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.run_button("sim/cockpit/electrical/battery_on", 7))
            tg.create_task(
                self.run_button("sim/cockpit/electrical/generator_on", 6, idx=0)
            )
            tg.create_task(
                self.run_button(
                    "simcoders/rep/cockpit2/engine/actuators/fuel_pump_0", 5
                )
            )
            tg.create_task(
                self.run_button("sim/cockpit/electrical/landing_lights_on", 4)
            )
            tg.create_task(
                self.run_button("sim/cockpit/electrical/beacon_lights_on", 2)
            )
            tg.create_task(
                self.run_button("sim/cockpit/electrical/strobe_lights_on", 1)
            )
            tg.create_task(self.run_button("sim/cockpit/switches/pitot_heat_on", 0))
