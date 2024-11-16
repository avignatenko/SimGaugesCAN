import logging
import asyncio

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
from .indicators1 import IndicatorsPanel1
from .indicators2 import IndicatorsPanel2
from .stec30alt import STec30Alt
from .leftbottompanel import LeftBottomPanel

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
        IndicatorsPanel1(sim, can),
        IndicatorsPanel2(sim, can),
        STec30Alt(sim, can),
        # low-left panel
        RPM(sim, can),
        MPR(sim, can),
        LeftBottomPanel(sim, can),
    ]


async def init():
    asyncio.gather(*map(lambda obj: obj.init(), _devices))
