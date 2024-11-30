import asyncio
import logging

from cansimconnector import cansimlib
from cansimconnector.arrowiiiturbodevices import busvolts

logger = logging.getLogger(__name__)


class LedGauge:
    def __init__(self, device: cansimlib.Device2, can_port, dataref, index=None):
        self._device = device
        self._dataref = dataref
        self._index = index
        self._can_port = can_port
        self._value_volts = None
        self._value_dataref = None

    async def run_volts(self):
        volts = await self._device.create_dataref_subscription(
            "sim/cockpit2/electrical/bus_volts", index=[0], tolerance=0.1
        )
        while True:
            self._value_volts = await volts.receive_new_value()
            await self._update_device()

    async def run_dataref(self):
        volts = await self._device.create_dataref_subscription(self._dataref, index=self._index, tolerance=0.1)
        while True:
            self._value_dataref = await volts.receive_new_value()
            await self._update_device()

    async def _update_device(self):
        led_value = self.is_light_on([self._value_volts, self._value_dataref])
        if led_value is None:
            return

        await self._device.can_send_byte(self._can_port, led_value)

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.run_volts())
            tg.create_task(self.run_dataref())

    @staticmethod
    def is_light_on(values: list):
        led = values[1]
        volts = values[0]
        if led is None or volts is None:
            return None

        return led if busvolts.electrics_on(volts) else 0


class LedGaugeMPR(LedGauge):
    MAX_MPR = 41

    @staticmethod
    def is_light_on(values: list):
        mpr = values[1]
        volts = values[0]

        if mpr is None or volts is None:
            return None

        return 1 if busvolts.electrics_on(volts) and mpr > LedGaugeMPR.MAX_MPR else 0


class Annunciators2(cansimlib.Device2):
    CAN_ID = 26

    def __init__(self, sim, can):
        super().__init__(sim, can)
        super().enable_rate_limiter(1000)
        super().set_can_id(self.CAN_ID)

    async def run(self):
        led_gauge = LedGauge(
            self,
            0,
            "sim/cockpit2/annunciators/gear_unsafe",
        )

        led_starter = LedGauge(
            self,
            1,
            "sim/cockpit2/engine/actuators/starter_hit",
            [0],
        )

        low_vacuum = LedGauge(self, 2, "sim/cockpit2/annunciators/low_vacuum")

        generator = LedGauge(self, 3, "sim/cockpit2/annunciators/generator")

        oil_pressure = LedGauge(
            self,
            4,
            "sim/cockpit2/annunciators/oil_pressure",
        )

        low_voltage = LedGauge(
            self,
            6,
            "sim/cockpit2/annunciators/low_voltage",
        )

        mpr_high = LedGaugeMPR(
            self,
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
