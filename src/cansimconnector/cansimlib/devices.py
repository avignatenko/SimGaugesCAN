from __future__ import annotations

import abc
import logging

from cansimconnector.cansimlib import canclient, xplanewsclient

logger = logging.getLogger(__name__)


class Device2:
    def __init__(self, sim: xplanewsclient.XPlaneClient, can: canclient.CANClient):
        self._sim = sim
        self._can = can

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

    @abc.abstractmethod
    async def run(self):
        pass
