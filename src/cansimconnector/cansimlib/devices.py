from __future__ import annotations

import abc
import logging

import asynciolimiter

from cansimconnector.cansimlib import canclient, xplanewsclient

logger = logging.getLogger(__name__)


class Device2:
    def __init__(self, sim: xplanewsclient.XPlaneClient, can: canclient.CANClient):
        self._sim = sim
        self._can = can
        self._rate_limiter = None
        self._can_id = None

    def enable_rate_limiter(self, rate):
        self._rate_limiter = asynciolimiter.StrictLimiter(rate)

    def set_can_id(self, can_id: int):
        self._can_id = can_id

    async def create_dataref_subscription(self, dataref_str, index: list[int] | None = None, tolerance=0.01):
        return await xplanewsclient.DatarefSubscription.create(
            self._sim,
            dataref_str,
            index,
            tolerance,
        )

    async def create_can_message_subscription(
        self,
        can_id,
        port,
        msg_type,
        compare: xplanewsclient.CANMessageSubscription.ValuePolicy = canclient.CANMessageSubscription.ValuePolicy.COMPARE,
    ) -> xplanewsclient.CANMessageSubscription:
        return await canclient.CANMessageSubscription.create(self._can, can_id, port, msg_type, compare)

    async def can_send_float(self, target_port: int, value: float):
        await self._can.send_float(self._can_id, target_port, value, self._rate_limiter)

    async def can_send_byte(self, target_port: int, value: int):
        await self._can.send_byte(self._can_id, target_port, value, self._rate_limiter)

    @abc.abstractmethod
    async def run(self):
        pass
