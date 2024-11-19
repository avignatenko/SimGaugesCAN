import asyncio

from .. import cansimlib


class BusVolts:

    def __init__(self, sim):
        self._sim: cansimlib.XPlaneClient = sim
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
