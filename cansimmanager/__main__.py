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

    logger.info("Reading config")
    config = common.read_config()

    # setup main objects
    logger.info("Making main objects")

    logger.info("Sim connection init")
    sim = Sim()
    while True:
        try:
            uri = config["simAddr"]
            await sim.connect(uri)
            break
        except (OSError, TimeoutError) as e:
            logger.error("Sim connection error: %s, reconnecting", e)
            continue

    logger.info("CAN bus init")

    try:
        can = Can()
        await can.connect(config["channel"], config["ttyBaudrate"])
        can.
    except Exception as e:
        logger.error("CAN error: %s", e)
        exit(-1)

    # subsribe devices
    logger.info("Registering devices")
    arrowiiiturbodevices.register(sim, can)
    await arrowiiiturbodevices.init()

    # run can receiver and websockets receiver async
    logger.info("Starting can and websockets listeners")
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(can.run())
        task2 = tg.create_task(sim.run())

if __name__ == "__main__":
    asyncio.run(main())
