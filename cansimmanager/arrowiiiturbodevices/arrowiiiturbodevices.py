import logging

from ..devices import Device
from ..sim import Sim
from ..can import Can

from .gyrosuction import GyroSuction
from .airspeed import Airspeed

logger = logging.getLogger(__name__)

_devices: list[Device] = []

def register(sim: Sim, can: Can):
    _devices.append(GyroSuction(sim, can))
    _devices.append(Airspeed(sim, can))

async def init():
    for device in _devices:
        await device.init()
