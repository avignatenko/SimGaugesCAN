import asyncio
import logging

from .. import cansimlib

logger = logging.getLogger(__name__)


class FuelQuantity0(cansimlib.SingleValueIndicator):
    def __init__(self, sim: cansimlib.XPlaneClient, can: cansimlib.CANClient):
        super().__init__(
            sim,
            can,
            can_id=25,
            port=2,
            dataref_str="simcoders/rep/indicators/fuel/fuel_quantity_ratio_0",
            idx=None,
            tolerance=0.1,
            dataref_to_value=lambda dataref: dataref * 40,
        )


class FuelQuantity1(cansimlib.SingleValueIndicator):
    def __init__(self, sim: cansimlib.XPlaneClient, can: cansimlib.CANClient):
        super().__init__(
            sim,
            can,
            can_id=25,
            port=0,
            dataref_str="simcoders/rep/indicators/fuel/fuel_quantity_ratio_1",
            idx=None,
            tolerance=0.1,
            dataref_to_value=lambda dataref: dataref * 40,
        )


class FuelPresss(cansimlib.SingleValueIndicator):
    def __init__(self, sim: cansimlib.XPlaneClient, can: cansimlib.CANClient):
        super().__init__(
            sim,
            can,
            can_id=25,
            port=1,
            dataref_str="simcoders/rep/cockpit2/gauges/indicators/fuel_press_psi_0",
            idx=None,
            tolerance=0.1,
        )


class IndicatorsPanel2(cansimlib.Device):

    def __init__(self, sim: cansimlib.XPlaneClient, can: cansimlib.CANClient):
        super().__init__(sim, can)

        self._devices = [
            FuelQuantity0(sim, can),
            FuelQuantity1(sim, can),
            FuelPresss(sim, can),
        ]

    async def init(self):
        asyncio.gather(*map(lambda obj: obj.init(), self._devices))
