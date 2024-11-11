import can
from .devices import Devices, Device


class GyroSuction(Device):

    def register(devices: Devices):
        devices.register_device(
            device=GyroSuction(),
            can_ids=[29],
            datarefs=["sim/cockpit2/gauges/indicators/airspeed_kts_pilot"],
        )

    async def handle_can_message(self, message: can.Message, sim) -> None:
        return

    async def handle_updated_dataref(self, dataref: str, bus: can.Bus) -> None:
        return


def register(devices: Devices):
    GyroSuction.register(devices)
