import logging
import asyncio

from ..devices import SingleValueIndicator, Device
from ..sim import Sim
from ..can import Can


logger = logging.getLogger(__name__)


class GeneratorAmps(SingleValueIndicator):
    async def init(self):
        await self._init_internal(
            can_id=27,
            port=0,
            dataref_str="sim/cockpit2/electrical/generator_amps",
            idx=0,
            tolerance=0.1,
        )


class OilTemp(SingleValueIndicator):
    async def init(self):
        await self._init_internal(
            can_id=27,
            port=1,
            dataref_str="simcoders/rep/engine/oil/temp_f_0",
            idx=None,
            tolerance=0.1,
        )


class OilPressure(SingleValueIndicator):
    async def init(self):
        await self._init_internal(
            can_id=27,
            port=2,
            dataref_str="simcoders/rep/engine/oil/press_psi_0",
            idx=None,
            tolerance=0.1,
        )


class OutsideAir(SingleValueIndicator):
    async def init(self):
        await self._init_internal(
            can_id=27,
            port=3,
            dataref_str="sim/cockpit2/temperature/outside_air_temp_degc",
            idx=None,
            tolerance=0.25,
        )


class FuelQuantity0(SingleValueIndicator):
    async def init(self):
        await self._init_internal(
            can_id=25,
            port=2,
            dataref_str="simcoders/rep/indicators/fuel/fuel_quantity_ratio_0",
            idx=None,
            tolerance=0.1,
            dataref_to_value=lambda dataref: dataref * 40,
        )


class FuelQuantity1(SingleValueIndicator):
    async def init(self):
        await self._init_internal(
            can_id=25,
            port=0,
            dataref_str="simcoders/rep/indicators/fuel/fuel_quantity_ratio_1",
            idx=None,
            tolerance=0.1,
            dataref_to_value=lambda dataref: dataref * 40,
        )


class FuelPresss(SingleValueIndicator):
    async def init(self):
        await self._init_internal(
            can_id=25,
            port=1,
            dataref_str="simcoders/rep/cockpit2/gauges/indicators/fuel_press_psi_0",
            idx=None,
            tolerance=0.1,
        )


class IndicatorsPanel(Device):

    def __init__(self, sim: Sim, can: Can):
        super().__init__(sim, can)

        self._devices = [
            GeneratorAmps(sim, can),
            OilTemp(sim, can),
            OilPressure(sim, can),
            OutsideAir(sim, can),
            FuelQuantity0(sim, can),
            FuelQuantity1(sim, can),
        ]

    async def init(self):
        asyncio.gather(*map(lambda obj: obj.init(), self._devices))
