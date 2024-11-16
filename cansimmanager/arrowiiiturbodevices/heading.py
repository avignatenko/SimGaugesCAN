import logging
import asyncio

from .. import common
from ..devices import Device

logger = logging.getLogger(__name__)


class Heading(Device):

    CAN_ID = 20

    async def init(self):

        self._ap_bug_mag_dataref_id = await self._sim.get_dataref_id(
            "sim/cockpit/autopilot/heading_mag"
        )

        self._ap_bug_manual_knob_override_mode = False
        self._ap_bug_restore_sim_mode_task = None
        self._ap_bug_mag_current = None

        self._dg_drift_dataref_id = await self._sim.get_dataref_id(
            "sim/cockpit/gyros/dg_drift_vac_deg"
        )

        self._dg_drift_manual_knob_override_mode = False
        self._dg_drift_restore_sim_mode_task = None
        self._dg_drift_current = None

        await self._sim.subscribe_dataref(
            "sim/cockpit/gyros/psi_vac_ind_degm",
            None,
            self._on_heading_update,
            tolerance=0.1,
            freq=5,
        )

        await self._sim.subscribe_dataref(
            "sim/cockpit/autopilot/heading_mag",
            None,
            self._on_heading_ap_bug_update,
            tolerance=0.1,
            freq=5,
        )

        await self._sim.subscribe_dataref(
            "sim/cockpit/gyros/dg_drift_vac_deg",
            None,
            self._on_dg_drift_update,
            tolerance=0.01,
            freq=5,
        )

        await self._can.subscribe_message(self.CAN_ID, self._on_knobs_rotated)

    async def _on_dg_drift_update(self, value):
        logger.debug("update received!! %s", value)
        if self._dg_drift_manual_knob_override_mode:
            return
        self._dg_drift_current = value

    async def _on_heading_update(self, value):
        logger.debug("update received!! %s", value)
        await self._set_heading(value)

    async def _set_heading(self, value: float):
        await self._can.send(self.CAN_ID, 0, common.make_payload_float(value))

    async def _on_heading_ap_bug_update(self, value):
        logger.debug("update received!! %s", value)
        if self._ap_bug_manual_knob_override_mode:
            return
        self._ap_bug_mag_current = value
        await self._set_heading_ap_bug(value)

    async def _set_heading_ap_bug(self, value: float):
        await self._can.send(self.CAN_ID, 1, common.make_payload_float(value))

    async def _on_knobs_rotated(self, port, payload):
        value = common.payload_float(payload)
        if port == 1:
            await self.on_ap_heading_knob_rotated(value)
        if port == 0:
            await self.on_dg_drift_adj_knob_rotated(value)

    async def on_dg_drift_adj_knob_rotated(self, value):
        if not self._dg_drift_current:
            return
        if self._dg_drift_restore_sim_mode_task:
            self._dg_drift_restore_sim_mode_task.cancel()
        self._dg_drift_manual_knob_override_mode = True
        self._dg_drift_current += value

        await self._sim.send_dataref(
            self._dg_drift_dataref_id, None, self._dg_drift_current
        )
        logger.debug("update sent!! %s", self._dg_drift_current)
        self._dg_drift_restore_sim_mode_task = asyncio.create_task(
            self.restore_sim_mode_dg_drift_mag()
        )

    async def on_ap_heading_knob_rotated(self, value):
        if not self._ap_bug_mag_current:
            return
        if self._ap_bug_restore_sim_mode_task:
            self._ap_bug_restore_sim_mode_task.cancel()
        self._ap_bug_manual_knob_override_mode = True
        self._ap_bug_mag_current += value
        await self._set_heading_ap_bug(self._ap_bug_mag_current)
        await self._sim.send_dataref(
            self._ap_bug_mag_dataref_id, None, self._ap_bug_mag_current
        )
        logger.debug("update sent!! %s", self._ap_bug_mag_current)
        self._ap_bug_restore_sim_mode_task = asyncio.create_task(
            self.restore_sim_mode_ap_bug_mag()
        )

    async def restore_sim_mode_dg_drift_mag(self):
        await asyncio.sleep(0.5)
        self._dg_drift_manual_knob_override_mode = False

    async def restore_sim_mode_ap_bug_mag(self):
        await asyncio.sleep(0.5)
        self._ap_bug_manual_knob_override_mode = False
