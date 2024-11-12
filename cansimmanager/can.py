import can
import logging
import asyncio
from typing import Callable

from . import common

logger = logging.getLogger(__name__)


class Can:

    def __init__(self):
        self._bus: can.interface.Bus = None
        self._callbacks = {}

    async def connect(self, channel, tty_baudrate):
        """
        bus = can.interface.Bus("test", bustype="virtual")
        bus_test_sender = can.interface.Bus('test', bustype='virtual')
        bus_test_sender.send(common.make_message(29, 0, 0, 0, []))
        """

        self._bus = can.interface.Bus(
            interface="slcan",
            channel=channel,
            ttyBaudrate=tty_baudrate,
            bitrate=1000000,
        )

    async def send(self, target_id: int, target_port: int, payload: list):
        common.send_command(
            self._bus,
            id_src=1,
            id_dst=target_id,
            priority=0,
            port=target_port,
            payload=payload,
        )

    async def subscribe_message(self, can_id: int, function: Callable):
        self._callbacks.setdefault(can_id, []).append(function)

    async def run(self):
        reader = can.AsyncBufferedReader()
        loop = asyncio.get_running_loop()
        notifier = can.Notifier(self._bus, listeners=[reader], loop=loop)

        logger.info("Starting CAN handler")

        while True:
            message = await reader.get_message()
            logger.debug("CAN message: %s", message.arbitration_id)

            callbacks = self._callbacks.get(
                common.src_id_from_canid(message.arbitration_id)
            )
            if not callbacks:
                continue

            for callback in callbacks:
                asyncio.create_task(callback(message.data))

        notifier.stop()
