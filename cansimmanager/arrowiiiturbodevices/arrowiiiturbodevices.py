import logging

from ..devices import Device
from ..sim import Sim
from ..can import Can

from .gyrosuction import GyroSuction
from .airspeed import Airspeed
from .turnroll import TurnRoll
from .attitude import Attitude

logger = logging.getLogger(__name__)

_devices: list[Device] = []

def register(sim: Sim, can: Can):
    # upper-left panel
    _devices.append(GyroSuction(sim, can))
    _devices.append(Airspeed(sim, can))
    _devices.append(TurnRoll(sim, can))
    _devices.append(Attitude(sim, can))

async def init():
    for device in _devices:
        await device.init()
