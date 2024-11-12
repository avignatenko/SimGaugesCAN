import logging
import asyncio

from .. import common
from ..devices import Device

logger = logging.getLogger(__name__)


class Heading(Device):

    CAN_ID = 20

    async def init(self):

        self._ap_heading_mag_dataref_id = await self._sim.get_dataref_id(
            "sim/cockpit/autopilot/heading_mag"
        )

        self._manual_knob_override_mode = False

        self._ap_heading_mag_current = None

        self._restore_sim_mode_task = None
        # await self._sim.subscribe_dataref(
        #    "sim/cockpit/gyros/psi_vac_ind_degm",
        #    self._on_heading_update,
        #    tolerance=0.1,
        #    freq=5,
        # )

        await self._sim.subscribe_dataref(
            "sim/cockpit/autopilot/heading_mag",
            self._on_heading_ap_bug_update,
            tolerance=0.1,
            freq=5,
        )

        await self._can.subscribe_message(self.CAN_ID, self._on_knobs_rotated)

    async def _on_heading_update(self, value):
        logging.debug("update received!! %s", value)
        await self._set_heading(value)

    async def _set_heading(self, value: float):
        await self._can.send(self.CAN_ID, 0, common.make_payload_float(value))

    async def _on_heading_ap_bug_update(self, value):
        logging.debug("update received!! %s", value)
        if self._manual_knob_override_mode : 
            return
        self._ap_heading_mag_current = value
        await self._set_heading_ap_bug(value)

    async def _set_heading_ap_bug(self, value: float):
        await self._can.send(self.CAN_ID, 1, common.make_payload_float(value))

    async def _on_knobs_rotated(self, port, payload):
        value = common.payload_float(payload)
        if port == 1:
            if not self._ap_heading_mag_current:
                return
            (
                self._restore_sim_mode_task.cancel()
                if self._restore_sim_mode_task
                else None
            )
            self._manual_knob_override_mode = True
            self._ap_heading_mag_current += value 
            await self._set_heading_ap_bug(self._ap_heading_mag_current)
            
            await self._sim.send_dataref(
                self._ap_heading_mag_dataref_id, self._ap_heading_mag_current
            )
            logging.debug("update sent!! %s", self._ap_heading_mag_current)
            self._restore_sim_mode_task = asyncio.create_task(self.restore_sim_mode())

    async def restore_sim_mode(self):
        await asyncio.sleep(0.5)
        self._manual_knob_override_mode = False
