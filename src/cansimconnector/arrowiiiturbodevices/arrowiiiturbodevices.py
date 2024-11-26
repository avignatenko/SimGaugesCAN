import asyncio
import logging

from cansimconnector import cansimlib
from cansimconnector.arrowiiiturbodevices.airspeed import Airspeed2
from cansimconnector.arrowiiiturbodevices.altitude import Altitude2
from cansimconnector.arrowiiiturbodevices.annunciators import Annunciators2
from cansimconnector.arrowiiiturbodevices.attitude import Attitude2
from cansimconnector.arrowiiiturbodevices.buttonspanel import ButtonsPanel2
from cansimconnector.arrowiiiturbodevices.fuelselector import FuelSelector2
from cansimconnector.arrowiiiturbodevices.gyrosuction import GyroSuction2
from cansimconnector.arrowiiiturbodevices.heading import Heading2
from cansimconnector.arrowiiiturbodevices.indicators1 import IndicatorsPanel1_2
from cansimconnector.arrowiiiturbodevices.indicators2 import IndicatorsPanel2_2
from cansimconnector.arrowiiiturbodevices.leftbottompanel import LeftBottomPane2
from cansimconnector.arrowiiiturbodevices.mpr import MPR2
from cansimconnector.arrowiiiturbodevices.rpm import RPM2
from cansimconnector.arrowiiiturbodevices.stec30alt import STec30Alt2
from cansimconnector.arrowiiiturbodevices.transponder import Transponder2
from cansimconnector.arrowiiiturbodevices.turnroll import TurnRoll2
from cansimconnector.arrowiiiturbodevices.vertspeed import VerticalSpeed2

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
    asyncio.gather(*(obj.init() for obj in _devices))


async def run():
    asyncio.gather(*(obj.run() for obj in _devices_2))
