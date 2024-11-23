import asyncio
import logging

from .. import cansimlib
from . import busvolts

logger = logging.getLogger(__name__)


class Annunciators(cansimlib.Device):
    CAN_ID = 26

    def __init__(self, sim: cansimlib.XPlaneClient, can: cansimlib.CANClient):
        super().__init__(sim, can)

        gear_unsafe = cansimlib.SingleValueIndicator(
            sim,
            can,
            can_id=self.CAN_ID,
            port=0,
            datarefs=[
                cansimlib.SingleValueIndicator.DatarefSubsription(
                    dataref_str="sim/cockpit2/annunciators/gear_unsafe",
                    idx=None,
                    tolerance=0.1,
                ),
                busvolts.bus_volts_subscription,
            ],
            dataref_to_value=lambda value, volts: (
                value if busvolts.electrics_on(volts) else 0
            ),
            type=cansimlib.SingleValueIndicator.CANType.BYTE,
        )

        starter_working = cansimlib.SingleValueIndicator(
            sim,
            can,
            can_id=self.CAN_ID,
            port=1,
            datarefs=[
                cansimlib.SingleValueIndicator.DatarefSubsription(
                    dataref_str="sim/cockpit2/engine/actuators/starter_hit",
                    idx=0,
                    tolerance=0.1,
                ),
                busvolts.bus_volts_subscription,
            ],
            dataref_to_value=lambda value, volts: (
                value if busvolts.electrics_on(volts) else 0
            ),
            type=cansimlib.SingleValueIndicator.CANType.BYTE,
        )

        low_vacuum = cansimlib.SingleValueIndicator(
            sim,
            can,
            can_id=self.CAN_ID,
            port=2,
            datarefs=[
                cansimlib.SingleValueIndicator.DatarefSubsription(
                    dataref_str="sim/cockpit2/annunciators/low_vacuum",
                    idx=None,
                    tolerance=0.1,
                ),
                busvolts.bus_volts_subscription,
            ],
            dataref_to_value=lambda value, volts: (
                value if busvolts.electrics_on(volts) else 0
            ),
            type=cansimlib.SingleValueIndicator.CANType.BYTE,
        )

        generator = cansimlib.SingleValueIndicator(
            sim,
            can,
            can_id=self.CAN_ID,
            port=3,
            datarefs=[
                cansimlib.SingleValueIndicator.DatarefSubsription(
                    dataref_str="sim/cockpit2/annunciators/generator",
                    idx=None,
                    tolerance=0.1,
                ),
                busvolts.bus_volts_subscription,
            ],
            dataref_to_value=lambda value, volts: (
                value if busvolts.electrics_on(volts) else 0
            ),
            type=cansimlib.SingleValueIndicator.CANType.BYTE,
        )

        oid_pressure = cansimlib.SingleValueIndicator(
            sim,
            can,
            can_id=self.CAN_ID,
            port=4,
            datarefs=[
                cansimlib.SingleValueIndicator.DatarefSubsription(
                    dataref_str="sim/cockpit2/annunciators/oil_pressure",
                    idx=None,
                    tolerance=0.1,
                ),
                busvolts.bus_volts_subscription,
            ],
            dataref_to_value=lambda value, volts: (
                value if busvolts.electrics_on(volts) else 0
            ),
            type=cansimlib.SingleValueIndicator.CANType.BYTE,
        )

        low_voltage = cansimlib.SingleValueIndicator(
            sim,
            can,
            can_id=self.CAN_ID,
            port=6,
            datarefs=[
                cansimlib.SingleValueIndicator.DatarefSubsription(
                    dataref_str="sim/cockpit2/annunciators/low_voltage",
                    idx=None,
                    tolerance=0.1,
                ),
                busvolts.bus_volts_subscription,
            ],
            dataref_to_value=lambda value, volts: (
                value if busvolts.electrics_on(volts) else 0
            ),
            type=cansimlib.SingleValueIndicator.CANType.BYTE,
        )

        mpr = cansimlib.SingleValueIndicator(
            sim,
            can,
            can_id=self.CAN_ID,
            port=5,
            datarefs=[
                cansimlib.SingleValueIndicator.DatarefSubsription(
                    dataref_str="sim/cockpit2/engine/indicators/MPR_in_hg",
                    idx=0,
                    tolerance=0.1,
                ),
                busvolts.bus_volts_subscription,
            ],
            dataref_to_value=lambda value, volts: (
                1 if (busvolts.electrics_on(volts) and value > 41) else 0
            ),
            type=cansimlib.SingleValueIndicator.CANType.BYTE,
        )

        self._devices = [
            gear_unsafe,
            starter_working,
            low_vacuum,
            generator,
            oid_pressure,
            low_voltage,
            mpr,
        ]

    async def init(self):
        asyncio.gather(*map(lambda obj: obj.init(), self._devices))
