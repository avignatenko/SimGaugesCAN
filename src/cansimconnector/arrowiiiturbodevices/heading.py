import asyncio
import logging

from cansimconnector import cansimlib

logger = logging.getLogger(__name__)


class Heading2(cansimlib.Device):
    def __init__(self, sim, can):
        super().__init__(sim, can, can_id=20)
        self._ap_bug_manual_knob_override_mode = False
        self._ap_bug_restore_sim_mode_task = None
        self._ap_bug_mag_current = None

        self._dg_drift_manual_knob_override_mode = False
        self._dg_drift_restore_sim_mode_task = None
        self._dg_drift_current = None

    async def _run_heading_update(self):
        dataref = await self.create_dataref_subscription("sim/cockpit/gyros/psi_vac_ind_degm", tolerance=0.1)

        while True:
            value = await dataref.receive_new_value()
            await self.can_send_float(0, value)

    async def _run_ap_bug_update(self):
        dataref = await self.create_dataref_subscription("sim/cockpit/autopilot/heading_mag", tolerance=0.1)

        while True:
            value = await dataref.receive_new_value()

            if self._ap_bug_manual_knob_override_mode:
                continue

            self._ap_bug_mag_current = value

            await self.can_send_float(1, value)

    async def _run_dg_drift_update(self):
        dataref = await self.create_dataref_subscription("sim/cockpit/gyros/dg_drift_vac_deg")

        while True:
            value = await dataref.receive_new_value()

            if self._dg_drift_manual_knob_override_mode:
                continue
            self._dg_drift_current = value

    async def _run_dg_drift_knob_update(self):
        can_message = await self.create_can_message_subscription2(
            0,
            cansimlib.CANMessageSubscription.CANType.FLOAT,
            compare=cansimlib.CANMessageSubscription.ValuePolicy.SEND_ALWAYS,
        )

        dg_drift_dataref_id = await self._sim.get_dataref_id("sim/cockpit/gyros/dg_drift_vac_deg")

        while True:
            value = await can_message.receive_new_value()

            if self._dg_drift_restore_sim_mode_task:
                self._dg_drift_restore_sim_mode_task.cancel()
            self._dg_drift_manual_knob_override_mode = True
            self._dg_drift_current += value
            self._dg_drift_current %= 360

            await self._sim.send_dataref(dg_drift_dataref_id, self._dg_drift_current)
            logger.debug("update sent!! %s", self._dg_drift_current)
            self._dg_drift_restore_sim_mode_task = asyncio.create_task(self._restore_sim_mode_dg_drift_mag())

    async def _run_dg_ap_bug_knob_update(self):
        can_message = await self.create_can_message_subscription2(
            1,
            cansimlib.CANMessageSubscription.CANType.FLOAT,
            compare=cansimlib.CANMessageSubscription.ValuePolicy.SEND_ALWAYS,
        )

        ap_bug_mag_dataref_id = await self._sim.get_dataref_id("sim/cockpit/autopilot/heading_mag")

        while True:
            value = await can_message.receive_new_value()
            if self._ap_bug_mag_current is None:
                continue

            if self._ap_bug_restore_sim_mode_task:
                self._ap_bug_restore_sim_mode_task.cancel()
            self._ap_bug_manual_knob_override_mode = True
            self._ap_bug_mag_current += value
            self._ap_bug_mag_current %= 360
            await self.can_send_float(1, self._ap_bug_mag_current)
            await self._sim.send_dataref(ap_bug_mag_dataref_id, self._ap_bug_mag_current)
            logger.debug("update sent!! %s", self._ap_bug_mag_current)
            self._ap_bug_restore_sim_mode_task = asyncio.create_task(self._restore_sim_mode_ap_bug_mag())

    async def _restore_sim_mode_dg_drift_mag(self):
        await asyncio.sleep(0.5)
        self._dg_drift_manual_knob_override_mode = False

    async def _restore_sim_mode_ap_bug_mag(self):
        await asyncio.sleep(0.5)
        self._ap_bug_manual_knob_override_mode = False

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._run_heading_update())
            tg.create_task(self._run_ap_bug_update())
            tg.create_task(self._run_dg_drift_update())
            tg.create_task(self._run_dg_drift_knob_update())
            tg.create_task(self._run_dg_ap_bug_knob_update())
