import asyncio
import logging

from .. import cansimlib
from .airspeed import Airspeed, Airspeed2
from .altitude import Altitude, Altitude2
from .annunciators import Annunciators, Annunciators2
from .attitude import Attitude
from .buttonspanel import ButtonsPanel
from .fuelselector import FuelSelector
from .gyrosuction import GyroSuction
from .heading import Heading
from .indicators1 import IndicatorsPanel1
from .indicators2 import IndicatorsPanel2
from .leftbottompanel import LeftBottomPanel
from .mpr import MPR
from .rpm import RPM
from .stec30alt import STec30Alt
from .transponder import Transponder, Transponder2
from .turnroll import TurnRoll
from .vertspeed import VerticalSpeed

logger = logging.getLogger(__name__)
_devices = []
_devices_2 = []


def register(sim: cansimlib.XPlaneClient, can: cansimlib.CANClient):
    global _devices
    global _devices_2

    _devices = [
        # upper-left panel
        GyroSuction(sim, can),
        # Airspeed(sim, can),
        TurnRoll(sim, can),
        Attitude(sim, can),
        # Altitude(sim, can),
        VerticalSpeed(sim, can),
        Heading(sim, can),
        IndicatorsPanel1(sim, can),
        IndicatorsPanel2(sim, can),
        STec30Alt(sim, can),
        #   Annunciators(sim, can),
        # low-left panel
        RPM(sim, can),
        MPR(sim, can),
        LeftBottomPanel(sim, can),
        # bottom
        FuelSelector(sim, can),
        # right
        ButtonsPanel(sim, can),
        # Transponder(sim, can),
    ]

    _devices_2 = [
        Airspeed2(sim, can),
        Altitude2(sim, can),
        Annunciators2(sim, can),
        Transponder2(sim, can),
    ]
    # _devices_2 = [Annunciators2(sim, can)]


async def init():
    asyncio.gather(*map(lambda obj: obj.init(), _devices))


async def run():
    asyncio.gather(*map(lambda obj: obj.run(), _devices_2))
