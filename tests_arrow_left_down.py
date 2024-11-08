# viewer python -m can.viewer -i slcan -b 1000000 -c '/dev/tty.usbmodem1101@4000000'
# 1 Mbit/second
# 115200 BIT / second = 0.1152 Mbit / second
# Standard values above 115200, such as: 230400, 460800, 500000, 576000, 921600, 1000000, 1152000, 1500000, 2000000, 2500000, 3000000, 3500000, 4000000 also work on many platforms and devices.

import can
import time
import unittest

from common import *


def setUpModule():
    global bus
    bus = can.interface.Bus(
        interface="slcan",
        channel="/dev/tty.usbmodem1101",
        ttyBaudrate=4000000,
        bitrate=1000000,
    )


def tearDownModule():
    bus.shutdown()


class BaseGaugeTest(unittest.TestCase):
    def send_command_2(self, port, payload):
        send_command(
            bus, id_src=1, id_dst=self.gauge_id, priority=0, port=port, payload=payload
        )


class ManPressTest(BaseGaugeTest):

    gauge_id = 22

    def test_man_press(self):
        self.send_command_2(port=0, payload=make_payload_float(20))
        time.sleep(2)
        self.send_command_2(port=0, payload=make_payload_float(45))
        time.sleep(2)
        self.send_command_2(port=0, payload=make_payload_float(30))
        time.sleep(2)
        self.send_command_2(port=0, payload=make_payload_float(0))

    def test_hallons_per_hour(self):
        self.send_command_2(port=1, payload=make_payload_float(20))
        time.sleep(2)
        self.send_command_2(port=1, payload=make_payload_float(15))
        time.sleep(2)
        self.send_command_2(port=1, payload=make_payload_float(10))
        time.sleep(2)
        self.send_command_2(port=1, payload=make_payload_float(0))

class RPMTest(BaseGaugeTest):

    gauge_id = 21

    def test_man_press(self):
        self.send_command_2(port=0, payload=make_payload_float(3500))
        time.sleep(2)
        self.send_command_2(port=0, payload=make_payload_float(2000))
        time.sleep(2)
        self.send_command_2(port=0, payload=make_payload_float(1500))
        time.sleep(2)
        self.send_command_2(port=0, payload=make_payload_float(0))

  
if __name__ == "__main__":
    unittest.main()
