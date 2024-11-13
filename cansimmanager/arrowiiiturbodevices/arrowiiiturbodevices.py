import logging
import asyncio

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
from .rpm import RPM
from .mpr import MPR
from .indicators import IndicatorsPanel

logger = logging.getLogger(__name__)


def register(sim: Sim, can: Can):
    global _devices

    _devices = [
        # upper-left panel
        GyroSuction(sim, can),
        Airspeed(sim, can),
        TurnRoll(sim, can),
        Attitude(sim, can),
        Altitude(sim, can),
        VerticalSpeed(sim, can),
        Heading(sim, can),
        IndicatorsPanel(sim, can),
        # low-left panel
        RPM(sim, can),
        MPR(sim, can),
    ]


async def init():
    asyncio.gather(*map(lambda obj: obj.init(), _devices))
