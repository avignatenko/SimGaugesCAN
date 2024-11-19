import asyncio
import logging

from .. import cansimlib

logger = logging.getLogger(__name__)


class GeneratorAmps(cansimlib.SingleValueIndicator):

    def __init__(self, sim: cansimlib.XPlaneClient, can: cansimlib.CANClient):
        super().__init__(
            sim,
            can,
            can_id=27,
            port=0,
            dataref_str="sim/cockpit2/electrical/generator_amps",
            idx=0,
            tolerance=0.1,
        )


class OilTemp(cansimlib.SingleValueIndicator):
    def __init__(self, sim: cansimlib.XPlaneClient, can: cansimlib.CANClient):
        super().__init__(
            sim,
            can,
            can_id=27,
            port=1,
            dataref_str="simcoders/rep/engine/oil/temp_f_0",
            idx=None,
            tolerance=0.1,
        )


class OilPressure(cansimlib.SingleValueIndicator):
    def __init__(self, sim: cansimlib.XPlaneClient, can: cansimlib.CANClient):
        super().__init__(
            sim,
            can,
            can_id=27,
            port=2,
            dataref_str="simcoders/rep/engine/oil/press_psi_0",
            idx=None,
            tolerance=0.1,
        )


class OutsideAir(cansimlib.SingleValueIndicator):
    def __init__(self, sim: cansimlib.XPlaneClient, can: cansimlib.CANClient):
        super().__init__(
            sim,
            can,
            can_id=27,
            port=3,
            dataref_str="sim/cockpit2/temperature/outside_air_temp_degc",
            idx=None,
            tolerance=0.25,
        )


class IndicatorsPanel1(cansimlib.Device):

    def __init__(self, sim: cansimlib.XPlaneClient, can: cansimlib.CANClient):
        super().__init__(sim, can)

        self._devices = [
            GeneratorAmps(sim, can),
            OilTemp(sim, can),
            OilPressure(sim, can),
            OutsideAir(sim, can),
        ]

    async def init(self):
        asyncio.gather(*map(lambda obj: obj.init(), self._devices))
