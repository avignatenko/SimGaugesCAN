# print(f"Invoking __main__.py for {__name__}")

import asyncio
import logging
import sys

logger = logging.getLogger(__name__)

from .common import *


async def can_consumer_handler(bus, sim, devices):
    reader = can.AsyncBufferedReader()
    loop = asyncio.get_running_loop()
    notifier = can.Notifier(bus, listeners=[reader], loop=loop)

    while True:
        # Wait for next message from AsyncBufferedReader
        message = await reader.get_message()
        print("CONSUMER")
        print(f"message received to process: {message.arbitration_id}")
        # 1) choose handler based on source id
        # 2) update dataref/call in simulator
        for device in devices.get_from_cansim_id(src_id_from_canid(message.arbitration_id)):
            await device.handle_can_message(message, sim)

    # Clean-up
    notifier.stop()

async def can_producer_handler(bus, sim, devices):
    while True:
        print("PRODUCER")
        dataref = await sim.get_updated_dataref()
        for device in devices.get_from_dataref(dataref):
            await device.handle_updated_dataref(dataref, bus)
      
async def main() -> None:
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    config = read_config()
    bus = can.interface.Bus(
        interface="slcan",
        channel=config["channel"],
        ttyBaudrate=config["ttyBaudrate"],
        bitrate=1000000,
    )

    # enable voltage
    # send_command(bus, 1, 31, 0, 1, make_payload_byte(12))
    # send_command(bus, 1, 31, 0, 2, make_payload_byte(1))

    await asyncio.gather(
        can_consumer_handler(bus=bus, sim=None, devices=None),
        can_producer_handler(bus=bus, sim=None, devices=None),
    )

    bus.shutdown()


if __name__ == "__main__":
    print("main script will be here in future")
    asyncio.run(main())
