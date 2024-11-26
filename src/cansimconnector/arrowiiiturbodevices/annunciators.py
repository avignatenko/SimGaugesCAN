import asyncio
import logging

from cansimconnector import cansimlib
from cansimconnector.arrowiiiturbodevices import busvolts

logger = logging.getLogger(__name__)


class LedGauge(cansimlib.Device2):

    def __init__(self, sim, can, can_id, can_port, dataref, index=None):
        super().__init__(sim, can)
        self._dataref = dataref
        self._index = index
        self._canid = can_id
        self._can_port = can_port
        self._value_volts = None
        self._value_dataref = None

    async def run_volts(self):
        volts = await self.create_dataref_subscription(
            "sim/cockpit2/electrical/bus_volts", index=[0], tolerance=0.1
        )
        while True:
            self._value_volts = await volts.receive_new_value()
            await self._update_device()

    async def run_dataref(self):
        volts = await self.create_dataref_subscription(
            self._dataref, index=self._index, tolerance=0.1
        )
        while True:
            self._value_dataref = await volts.receive_new_value()
            await self._update_device()

    async def _update_device(self):
        led_value = self.is_light_on([self._value_volts, self._value_dataref])
        if led_value is None:
            return

        logger.debug(
            "id: %s, port: %s, value: %s", self._canid, self._can_port, led_value
        )
        await self._can.send(
            self._canid, self._can_port, cansimlib.make_payload_byte(led_value)
        )

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.run_volts())
            tg.create_task(self.run_dataref())

    def is_light_on(self, values: list):
        led = values[1]
        volts = values[0]
        if led is None or volts is None:
            return None

        return led if busvolts.electrics_on(volts) else 0


class LedGaugeMPR(LedGauge):

    MAX_MPR = 41

    def is_light_on(self, values: list):
        mpr = values[1]
        volts = values[0]

        if mpr is None or volts is None:
            return None

        return 1 if busvolts.electrics_on(volts) and mpr > self.MAX_MPR else 0


class Annunciators2(cansimlib.Device2):
    CAN_ID = 26

    async def run(self):
        led_gauge = LedGauge(
            self._sim,
            self._can,
            self.CAN_ID,
            0,
            "sim/cockpit2/annunciators/gear_unsafe",
        )

        led_starter = LedGauge(
            self._sim,
            self._can,
            self.CAN_ID,
            1,
            "sim/cockpit2/engine/actuators/starter_hit",
            [0],
        )

        low_vacuum = LedGauge(
            self._sim, self._can, self.CAN_ID, 2, "sim/cockpit2/annunciators/low_vacuum"
        )

        generator = LedGauge(
            self._sim, self._can, self.CAN_ID, 3, "sim/cockpit2/annunciators/generator"
        )

        oil_pressure = LedGauge(
            self._sim,
            self._can,
            self.CAN_ID,
            4,
            "sim/cockpit2/annunciators/oil_pressure",
        )

        low_voltage = LedGauge(
            self._sim,
            self._can,
            self.CAN_ID,
            6,
            "sim/cockpit2/annunciators/low_voltage",
        )

        mpr_high = LedGaugeMPR(
            self._sim,
            self._can,
            self.CAN_ID,
            5,
            "sim/cockpit2/engine/indicators/MPR_in_hg",
            index=[0],
        )

        async with asyncio.TaskGroup() as tg:
            tg.create_task(led_gauge.run())
            tg.create_task(led_starter.run())
            tg.create_task(low_vacuum.run())
            tg.create_task(generator.run())
            tg.create_task(oil_pressure.run())
            tg.create_task(low_voltage.run())
            tg.create_task(mpr_high.run())


class Annunciators(cansimlib.Device):
    CAN_ID = 26
    MAX_MPR = 41

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
            can_type=cansimlib.SingleValueIndicator.CANType.BYTE,
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
            can_type=cansimlib.SingleValueIndicator.CANType.BYTE,
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
            can_type=cansimlib.SingleValueIndicator.CANType.BYTE,
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
            can_type=cansimlib.SingleValueIndicator.CANType.BYTE,
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
            can_type=cansimlib.SingleValueIndicator.CANType.BYTE,
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
            can_type=cansimlib.SingleValueIndicator.CANType.BYTE,
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
                1 if (busvolts.electrics_on(volts) and value > self.MAX_MPR) else 0
            ),
            can_type=cansimlib.SingleValueIndicator.CANType.BYTE,
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
        asyncio.gather(*(obj.init() for obj in self._devices))
