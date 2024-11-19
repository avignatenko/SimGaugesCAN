import asyncio
import logging

from .. import cansimlib

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
        asyncio.gather(*map(lambda obj: obj.init(), self._devices))
