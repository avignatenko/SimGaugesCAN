import asyncio

from .. import cansimlib

bus_volts_subscription = cansimlib.SingleValueIndicator.DatarefSubsription(
    dataref_str="sim/cockpit2/electrical/bus_volts",
    idx=0,
    tolerance=0.1,
)


def electrics_on(volts):
    return volts > 5


class BusVolts:

    def __init__(self, sim):
        self._sim: cansimlib.XPlaneClient = sim
        self._volts = 0
        self._volts_ok = False
        self._callbacks_status = []
        self._callbacks = []

    async def init(self):
        await self._sim.subscribe_dataref(
            "sim/cockpit2/electrical/bus_volts",
            None,
            self._on_bus_volts,
            tolerance=0.1,
            freq=1,
        )

    async def _on_bus_volts(self, value):
        self._volts = value[0]

        asyncio.gather(*map(lambda callback: callback(self._volts), self._callbacks))

        new_volts_ok = electrics_on(self._volts)
        if self._volts_ok != new_volts_ok:
            self._volts_ok = new_volts_ok

            asyncio.gather(
                *map(lambda callback: callback(new_volts_ok), self._callbacks_status)
            )

    def bus_volts_ok(self):
        return self._volts_ok

    def register_ok_status_change(self, callback):
        self._callbacks_status.append(callback)

    def register_change(self, callback):
        self._callbacks.append(callback)
