import asyncio
import logging
import sys

import click

from cansimconnector import arrowiiiturbodevices, cansimlib
from cansimconnector.__about__ import __version__

if sys.platform in {"win32", "cygwin", "cli"}:
    from winloop import run  # type: ignore
else:
    # if we're on apple or linux do this instead
    from uvloop import run  # type: ignore

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
            logger.error("Sim connection to %s error: %s, reconnecting", config["simAddr"], e)  # noqa: TRY400
            await asyncio.sleep(5.0)
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
            logger.error("CAN error: %s, reconnecting", e)  # noqa: TRY400
            # CAN doesnt have connection timeout, so we'll wait here
            await asyncio.sleep(5.0)
            continue
    return can


async def main_loop() -> None:
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    asyncio.get_event_loop().slow_callback_duration = 15  # all callbacks should fit into 15ms

    logger.info("Reading config")
    config = cansimlib.read_config()

    # setup main objects
    logger.info("Connecting to services")

    async with asyncio.TaskGroup() as tg:
        task_sim = tg.create_task(connect_sim(config))
        task_can = tg.create_task(connect_can(config))

    sim = task_sim.result()
    can = task_can.result()

    logger.info("Connected to services")

    # subsribe devices
    logger.info("Registering devices")
    devices = arrowiiiturbodevices.Devices()
    devices.arrowiiiturbodevices.register(sim, can)

    # run can receiver and websockets receiver async
    logger.info("Starting main loop")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(devices.run())
        tg.create_task(can.run())
        tg.create_task(sim.run())


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="CANSimConnector")
def cansimconnector():


    run(main_loop(), debug=True)
