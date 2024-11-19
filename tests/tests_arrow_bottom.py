# viewer python -m can.viewer -i slcan -b 1000000 -c '/dev/tty.usbmodem1101@4000000'

import time
import unittest

import can

import cansimconnector.cansimlib as cs


def setUpModule():
    global bus
    config = cs.read_config()
    bus = can.interface.Bus(
        interface="slcan",
        channel=config["channel"],
        ttyBaudrate=config["ttyBaudrate"],
        bitrate=1000000,
    )


def tearDownModule():
    bus.shutdown()


class BaseGaugeTest(unittest.TestCase):
    def send_command_2(self, port, payload):
        cs.send_command(
            bus,
            id_src=1,
            id_dst=self.gauge_id,
            priority=0,
            port=port,
            payload=payload,
        )


class FuelSelectorTest(BaseGaugeTest):

    gauge_id = 30

    def test_knob_manual(self):

        for msg in bus:
            if cs.src_id_from_canid(msg.arbitration_id) == self.gauge_id:
                print(msg.data)
                break


if __name__ == "__main__":
    unittest.main()
