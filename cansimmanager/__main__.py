import asyncio
import logging
import sys
import can
import uvloop

from . import common
from .devices import Devices
from .sim import Sim

from . import arrowiiiturbodevices

logger = logging.getLogger(__name__)


async def can_handler(bus: can.Bus, sim, devices: Devices):
    reader = can.AsyncBufferedReader()
    loop = asyncio.get_running_loop()
    notifier = can.Notifier(bus, listeners=[reader], loop=loop)

    while True:
        message = await reader.get_message()
        logger.debug("CAN message: %s", message.arbitration_id)
        cansim_id = common.src_id_from_canid(message.arbitration_id)
        for device in devices.get_from_cansim_id(cansim_id):
            await device.handle_can_message(message, sim)

    notifier.stop()


async def websockets_handler(bus, sim, devices):

    while True:
        dataref = await sim.get_updated_dataref()
        for device in devices.get_from_dataref(dataref):
            await device.handle_updated_dataref(dataref, bus)


async def main() -> None:
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    logging.info("Reading config")
    config = common.read_config()

    # setup main objects
    logging.info("Making main objects")

    logging.info("Registering devices")
    devices = Devices()
    arrowiiiturbodevices.register(devices)

    logging.info("Sim connection init")
    sim = Sim()
    try:
        uri = "ws://localhost:8765"
        #await sim.connect(uri)
    except OSError as e:
        logging.error("Sim error: %s", e)
        exit(-1)

    logging.info("CAN bus init")

    bus = can.interface.Bus("test", bustype="virtual")
    bus_test_sender = can.interface.Bus('test', bustype='virtual')
    bus_test_sender.send(common.make_message(29, 0, 0, 0, []))

    '''
    try:
        bus = can.interface.Bus(
            interface="slcan",
            channel=config["channel"],
            ttyBaudrate=config["ttyBaudrate"],
            bitrate=1000000,
        )
    except can.CanInitializationError as e:
        logging.error("CAN error: %s", e)
        bus.shutdown()
        exit(-1)
    '''

    # run can receiver and websockets receiver async
    logging.info("Starting can and websockets listeners")
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(can_handler(bus=bus, sim=sim, devices=devices))
        task2 = tg.create_task(websockets_handler(bus=bus, sim=sim, devices=devices))

    bus.shutdown()


if __name__ == "__main__":
    uvloop.run(main())
    #asyncio.run(main())
