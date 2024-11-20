import logging

from .. import cansimlib
from . import busvolts

logger = logging.getLogger(__name__)


class Transponder(cansimlib.Device):

    CAN_ID = 31

    async def init(self):

        self._bus_volts = busvolts.BusVolts(self._sim)
        self._bus_volts.register_change(self._on_volts_changed)
        await self._bus_volts.init()

        self._transponder_code_dataref_id = await self._sim.get_dataref_id(
            "sim/cockpit2/radios/actuators/transponder_code"
        )

        self._transponder_mode_dataref_id = await self._sim.get_dataref_id(
            "sim/cockpit2/radios/actuators/transponder_mode"
        )

        await self._can.subscribe_message_port(
            self.CAN_ID, 1, self._on_transponder_code
        )

        await self._can.subscribe_message_port(
            self.CAN_ID, 0, self._on_transponder_mode
        )

        await self._can.subscribe_message_port(
            self.CAN_ID, 2, self._on_transponder_ident
        )

        await self._sim.subscribe_dataref(
            "sim/cockpit2/radios/indicators/transponder_brightness",
            None,
            self._on_transponder_brightness,
            tolerance=0.1,
            freq=5,
        )

    async def _on_transponder_code(self, port, payload):

        squawk = cansimlib.payload_ushort(payload)
        await self._sim.send_dataref(self._transponder_code_dataref_id, None, squawk)

    async def _on_transponder_mode(self, port, payload):
        value = cansimlib.payload_byte(payload)
        await self._sim.send_dataref(self._transponder_mode_dataref_id, None, value - 1)

    async def _on_transponder_ident(self, port, payload):
        # value = cansimlib.payload_float(payload)
        # await self._sim.send_dataref(self._bar_in_hg_dataref_id, None, value)
        # xpl_command("sim/radios/transponder_ident")
        pass

    async def _on_transponder_brightness(self, value):
        await self._set_transponder_light(1 if value > 0.3 else 0)

    async def _set_transponder_light(self, value: int):
        await self._can.send(self.CAN_ID, 2, cansimlib.make_payload_byte(value))

    async def _on_volts_changed(self, value: float):
        await self._can.send(self.CAN_ID, 1, cansimlib.make_payload_byte(int(value)))
