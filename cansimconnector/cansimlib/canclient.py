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
        await self.subscribe_message_port(can_id, None, function)

    async def subscribe_message_port(self, can_id: int, port: int, function: Callable):
        canid_callbacks = self._callbacks.setdefault(can_id, {})
        port_callbacks = canid_callbacks.setdefault(port, [])
        port_callbacks.append(function)

    async def run(self):
        reader = can.AsyncBufferedReader()
        loop = asyncio.get_running_loop()
        notifier = can.Notifier(self._bus, listeners=[reader], loop=loop)

        logger.info("Starting CAN handler")

        background_tasks = set()

        while True:
            message = await reader.get_message()
            logger.debug("CAN message: %s", message.arbitration_id)

            src_id = common.src_id_from_canid(message.arbitration_id)
            port = common.port_from_canid(message.arbitration_id)

            canid_callbacks = self._callbacks.get(src_id)
            if not canid_callbacks:
                continue

            callbacks = canid_callbacks.get(None, []) + canid_callbacks.get(port, [])

            for callback in callbacks:
                task = asyncio.create_task(callback(port, message.data))
                background_tasks.add(task)
                task.add_done_callback(background_tasks.discard)

        notifier.stop()
