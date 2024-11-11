import asyncio
import logging
import sys

from . import common
from .sim import Sim
from .can import Can

from .arrowiiiturbodevices import arrowiiiturbodevices

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    logging.info("Reading config")
    config = common.read_config()

    # setup main objects
    logging.info("Making main objects")

    logging.info("Sim connection init")
    try:
        sim = Sim()
        uri = config["simAddr"]
        await sim.connect(uri)
    except OSError as e:
        logging.error("Sim error: %s", e)
        exit(-1)

    logging.info("CAN bus init")

    try:
        can = Can()
        await can.connect(config["channel"], config["ttyBaudrate"])
    except Exception as e:
        logging.error("CAN error: %s", e)
        exit(-1)

    # subsribe devices
    logging.info("Registering devices")
    arrowiiiturbodevices.register(sim, can)
    await arrowiiiturbodevices.init()

    # run can receiver and websockets receiver async
    logging.info("Starting can and websockets listeners")
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(can.run())
        task2 = tg.create_task(sim.run())

if __name__ == "__main__":
    asyncio.run(main())
