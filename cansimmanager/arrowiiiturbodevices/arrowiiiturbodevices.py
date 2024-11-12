import logging

from ..devices import Device
from ..sim import Sim
from ..can import Can

from .gyrosuction import GyroSuction
from .airspeed import Airspeed
from .turnroll import TurnRoll
from .attitude import Attitude
from .altitude import Altitude
from .vertspeed import VerticalSpeed
from .heading import Heading

logger = logging.getLogger(__name__)

_devices: list[Device] = []

def register(sim: Sim, can: Can):
    # upper-left panel
    _devices.append(GyroSuction(sim, can))
    _devices.append(Airspeed(sim, can))
    _devices.append(TurnRoll(sim, can))
    _devices.append(Attitude(sim, can))
    _devices.append(Altitude(sim, can))
    _devices.append(VerticalSpeed(sim, can))
    _devices.append(Heading(sim, can))
    
async def init():
    for device in _devices:
        await device.init()
