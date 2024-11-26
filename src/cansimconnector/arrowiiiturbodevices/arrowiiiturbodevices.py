import asyncio
import logging

from .. import cansimlib
from .airspeed import Airspeed2
from .altitude import Altitude2
from .annunciators import Annunciators2
from .attitude import Attitude2
from .buttonspanel import ButtonsPanel2
from .fuelselector import FuelSelector2
from .gyrosuction import GyroSuction2
from .heading import Heading2
from .indicators1 import IndicatorsPanel1_2
from .indicators2 import IndicatorsPanel2_2
from .leftbottompanel import LeftBottomPane2
from .mpr import MPR2
from .rpm import RPM2
from .stec30alt import STec30Alt2
from .transponder import Transponder2
from .turnroll import TurnRoll2
from .vertspeed import VerticalSpeed2

logger = logging.getLogger(__name__)
_devices = []
_devices_2 = []


def register(sim: cansimlib.XPlaneClient, can: cansimlib.CANClient):
    global _devices
    global _devices_2

    _devices = [
        # upper-left panel
        # GyroSuction(sim, can),
        # Airspeed(sim, can),
        # TurnRoll(sim, can),
        # Attitude(sim, can),
        # Altitude(sim, can),
        # VerticalSpeed(sim, can),
        # Heading(sim, can),
        # IndicatorsPanel1(sim, can),
        # IndicatorsPanel2(sim, can),
        # STec30Alt(sim, can),
        #   Annunciators(sim, can),
        # low-left panel
        # RPM(sim, can),
        # MPR(sim, can),
        # LeftBottomPanel(sim, can),
        # bottom
        # FuelSelector(sim, can),
        # right
        # ButtonsPanel(sim, can),
        # Transponder(sim, can),
    ]

    _devices_2 = [
        Airspeed2(sim, can),
        Altitude2(sim, can),
        Annunciators2(sim, can),
        Transponder2(sim, can),
        GyroSuction2(sim, can),
        TurnRoll2(sim, can),
        VerticalSpeed2(sim, can),
        Attitude2(sim, can),
        MPR2(sim, can),
        RPM2(sim, can),
        FuelSelector2(sim, can),
        ButtonsPanel2(sim, can),
        STec30Alt2(sim, can),
        IndicatorsPanel1_2(sim, can),
        IndicatorsPanel2_2(sim, can),
        LeftBottomPane2(sim, can),
        Heading2(sim, can),
    ]


async def init():
    asyncio.gather(*map(lambda obj: obj.init(), _devices))


async def run():
    asyncio.gather(*map(lambda obj: obj.run(), _devices_2))
