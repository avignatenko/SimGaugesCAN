import asyncio
import enum
import logging
from dataclasses import dataclass
from typing import Callable

import can

from . import common

logger = logging.getLogger(__name__)


class CANMessageSubscription:
    """Representation of receving message from CANSim"""

    class CANType(enum.Enum):
        """Set of different Cansim message types"""

        FLOAT = 1
        BYTE = 2
        USHORT = 3

    def __init__(self, can_bus, can_id, port, msg_type, compare: bool = True):
        self._can = can_bus
        self._id = can_id
        self._port = port
        self._msg_type = msg_type
        self._prev_payload = None
        self._compare = compare

    @classmethod
    async def create(cls, can_bus, can_id, port, msg_type, compare: bool = True):
        """Create can message, including registering subscription"""
        await can_bus.subscribe_message_port_no_callback(can_id, port)

        self = cls(can_bus, can_id, port, msg_type, compare)
        return self

    def _is_small_change(self, new_payload):

        if not self._prev_payload:
            return False

        return self._prev_payload == new_payload

    async def receive_new_payload(self):

        if not self._compare:
            return await self._can.wait_message(self._id, self._port)

        while True:
            payload = self._can.get_message(self._id, self._port)
            if payload is not None:
                if not self._is_small_change(payload):
                    self._prev_payload = payload
                    return payload

            await self._can.wait_message(self._id, self._port)

    async def receive_new_value(self):

        payload = await self.receive_new_payload()
        match self._msg_type:
            case self.CANType.FLOAT:
                return common.payload_float(payload)
            case self.CANType.BYTE:
                return common.payload_byte(payload)
            case self.CANType.USHORT:
                return common.payload_ushort(payload)
        return None


class CANClient:

    @dataclass
    class CANMessageData:
        value = None
        value_future: asyncio.Future = None

    def __init__(self):
        self._bus: can.interface.Bus = None
        self._callbacks = {}
        self._values: dict[self.CANMessageData] = {}

    def _init_bus(self, channel, tty_baudrate):
        self._bus = can.interface.Bus(
            interface="slcan",
            channel=channel,
            ttyBaudrate=tty_baudrate,
            bitrate=1000000,
        )

    async def connect(self, channel, tty_baudrate):
        self._init_bus(channel=channel, tty_baudrate=tty_baudrate)
        # await asyncio.get_running_loop().run_in_executor(
        #    None, self._init_bus, channel, tty_baudrate
        # )

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

    async def subscribe_message_port_no_callback(self, can_id: int, port: int):
        self._values.setdefault(
            (can_id, port),
            self.CANMessageData(asyncio.get_running_loop().create_future()),
        )

    def get_message(self, can_id: int, port: int):
        return self._values[(can_id, port)].value

    async def wait_message(self, can_id: int, port: int):
        return await self._values[(can_id, port)].value_future

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

            value = self._values.get((src_id, port))
            if value is None:
                logger.info(
                    "Received CAN value from %s, %s, but no subscribers", src_id, port
                )
                # continue
            else:
                value.value = message.data
                value.value_future.set_result(message.data)
                value.value_future = asyncio.get_running_loop().create_future()

            canid_callbacks = self._callbacks.get(src_id)
            if not canid_callbacks:
                continue

            callbacks = canid_callbacks.get(None, []) + canid_callbacks.get(port, [])

            for callback in callbacks:
                task = asyncio.create_task(callback(port, message.data))
                background_tasks.add(task)
                task.add_done_callback(background_tasks.discard)

        notifier.stop()
