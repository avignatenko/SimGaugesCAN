import can

import time
import unittest

from common import *

# tests!!


def setUpModule():
    global bus
    bus = can.interface.Bus(interface='slcan', channel='/dev/tty.usbmodem1101', bitrate=1000000)

def tearDownModule():
    bus.shutdown()

class BaseGaugeTest(unittest.TestCase):
    def send_command_2(self, port, payload):
        send_command(bus, id_src=1, id_dst=self.gauge_id, priority=0, port=port, payload=payload)
  
class GyroSuctionTests(BaseGaugeTest):
  
    gauge_id = 29

    def test_basic(self):
        self.send_command_2(port=0, payload=make_payload_float(2))
        time.sleep(1)
        self.send_command_2(port=0, payload=make_payload_float(4))
        time.sleep(1)
        self.send_command_2(port=0, payload=make_payload_float(6))
        time.sleep(1)
        self.send_command_2(port=0, payload=make_payload_float(0))
 
class AirspeedTests(BaseGaugeTest):
  
    gauge_id = 16

    def test_basic(self):
        self.send_command_2(port=0, payload=make_payload_float(20))
        time.sleep(1)
        self.send_command_2(port=0, payload=make_payload_float(40))
        time.sleep(1)
        self.send_command_2(port=0, payload=make_payload_float(100))
        time.sleep(1)
        self.send_command_2(port=0, payload=make_payload_float(0))
 
class AttIndicatorTests(BaseGaugeTest):
  
    gauge_id = 28

    def test_ver(self):
        self.send_command_2(port=0, payload=make_payload_float(-10))
        time.sleep(1)
        self.send_command_2(port=0, payload=make_payload_float(10))
        time.sleep(1)
        self.send_command_2(port=0, payload=make_payload_float(0))
 
    def test_hor(self):
        self.send_command_2(port=1, payload=make_payload_float(-50))
        time.sleep(1)
        self.send_command_2(port=1, payload=make_payload_float(50))
        time.sleep(1)
        self.send_command_2(port=1, payload=make_payload_float(0))


unittest.main() # run all tests