import asyncio
import logging
from typing import Callable

import can

from . import common

logger = logging.getLogger(__name__)


class CANClient:

    def __init__(self):
        self._bus: can.interface.Bus = None
        self._callbacks = {}

    async def connect(self, channel, tty_baudrate):
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
                asyncio.create_task(
                    callback(
                        common.port_from_canid(message.arbitration_id), message.data
                    )
                )

        notifier.stop()
