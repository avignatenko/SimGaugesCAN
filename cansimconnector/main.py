import asyncio
import logging
import sys

from . import arrowiiiturbodevices, cansimlib

logger = logging.getLogger(__name__)


async def connect_sim(config) -> cansimlib.XPlaneClient:
    logger.info("Sim connection init")
    sim = cansimlib.XPlaneClient()
    while True:
        try:
            uri = config["simAddr"]
            await sim.connect(uri)
            logger.info("Sim connected")
            break
        except (OSError, TimeoutError) as e:
            logger.error("Sim connection error: %s, reconnecting", e)
            continue
    return sim


async def connect_can(config) -> cansimlib.CANClient:
    logger.info("CAN bus init")
    can = cansimlib.CANClient()
    while True:
        try:
            await can.connect(config["channel"], config["ttyBaudrate"])
            logger.info("CAN connected")
            break
        except Exception as e:
            logger.error("CAN error: %s, reconnecting", e)
            asyncio.sleep(2.0)  # CAN doesnt have connection timeout, so we'll wait here
            continue
    return can


async def main_loop() -> None:
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    logger.info("Reading config")
    config = cansimlib.read_config()

    # setup main objects
    logger.info("Making main objects")

    sim = await connect_sim(config)
    can = await connect_can(config)

    # subsribe devices
    logger.info("Registering devices")
    arrowiiiturbodevices.register(sim, can)

    arrowiiiturbodevices
    logger.info("Devices init")
    await arrowiiiturbodevices.init()

    # run can receiver and websockets receiver async
    logger.info("Starting main loop")
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(can.run())
        task2 = tg.create_task(sim.run())


def main():
    asyncio.run(main_loop())


if __name__ == "__main__":
    main()
