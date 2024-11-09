# viewer python -m can.viewer -i slcan -b 1000000 -c '/dev/tty.usbmodem1101@4000000'
# 1 Mbit/second
# 115200 BIT / second = 0.1152 Mbit / second
# Standard values above 115200, such as: 230400, 460800, 500000, 576000, 921600, 1000000, 1152000, 1500000, 2000000, 2500000, 3000000, 3500000, 4000000 also work on many platforms and devices.

import can
import time
import unittest
import cansimmanager


def setUpModule():
    global bus
    config = cansimmanager.read_config()
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
        cansimmanager.send_command(
            bus,
            id_src=1,
            id_dst=self.gauge_id,
            priority=0,
            port=port,
            payload=payload,
        )


class GyroSuctionTests(BaseGaugeTest):

    gauge_id = 29

    def test_basic(self):
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(2))
        time.sleep(1)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(4))
        time.sleep(1)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(6))
        time.sleep(1)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(0))


class AirspeedTests(BaseGaugeTest):

    gauge_id = 16

    def test_basic(self):
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(20))
        time.sleep(1)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(40))
        time.sleep(1)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(100))
        time.sleep(1)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(0))


class AttIndicatorTests(BaseGaugeTest):

    gauge_id = 28

    def test_ver(self):
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(-30))
        time.sleep(1)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(30))
        time.sleep(1)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(0))

    def test_hor(self):
        self.send_command_2(port=1, payload=cansimmanager.make_payload_float(-30))
        time.sleep(1)
        self.send_command_2(port=1, payload=cansimmanager.make_payload_float(30))
        time.sleep(1)
        self.send_command_2(port=1, payload=cansimmanager.make_payload_float(0))


class AltimeterTests(BaseGaugeTest):

    gauge_id = 17

    def test_basic(self):
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(0))
        time.sleep(1)
        self.send_command_2(
            port=0, payload=cansimmanager.make_payload_float(-2000)
        )  # why - ???
        time.sleep(1)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(-5000))
        time.sleep(1)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(0))

    def test_knob_manual(self):

        for msg in bus:
            if cansimmanager.src_id_from_canid(msg.arbitration_id) == self.gauge_id:
                print(msg.data)
                break


class TurnCoordinatorTests(BaseGaugeTest):

    gauge_id = 19

    def test_ver(self):
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(-10))
        time.sleep(1)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(10))
        time.sleep(1)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(0))

    def test_hor(self):
        self.send_command_2(port=1, payload=cansimmanager.make_payload_float(-2))
        time.sleep(1)
        self.send_command_2(port=1, payload=cansimmanager.make_payload_float(2))
        time.sleep(1)
        self.send_command_2(port=1, payload=cansimmanager.make_payload_float(0))


class DirIndicatorTests(BaseGaugeTest):

    gauge_id = 20

    def test_ver(self):
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(-30))
        time.sleep(1)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(30))
        time.sleep(1)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(0))
  
    def test_hor(self):
        self.send_command_2(port=1, payload=cansimmanager.make_payload_float(-30))
        time.sleep(1)
        self.send_command_2(port=1, payload=cansimmanager.make_payload_float(30))
        time.sleep(1)
        self.send_command_2(port=1, payload=cansimmanager.make_payload_float(0))

    def test_knob_manual_0(self):

        for msg in bus:
            if (
                cansimmanager.src_id_from_canid(msg.arbitration_id) == self.gauge_id
                and cansimmanager.port_from_canid(msg.arbitration_id) == 0
            ):
                print(msg.data)
                break

    def test_knob_manual_1(self):

        for msg in bus:
            if (
                cansimmanager.src_id_from_canid(msg.arbitration_id) == self.gauge_id
                and cansimmanager.port_from_canid(msg.arbitration_id) == 1
            ):
                print(msg.data)
                break


class VertSpeedTests(BaseGaugeTest):

    gauge_id = 18

    def test_basic(self):
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(-15))
        time.sleep(2)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(15))
        time.sleep(2)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(0))


class ArrowUpperLedGaugeTests(BaseGaugeTest):

    gauge_id = 26

    def test_basic(self):
        for i in range(8):
            self.send_command_2(port=i, payload=cansimmanager.make_payload_byte(1))
            time.sleep(0.5)
        for i in range(8):
            self.send_command_2(port=i, payload=cansimmanager.make_payload_byte(0))
            time.sleep(0.5)

    def test_buttons_manual_0(self):

        for msg in bus:
            if (
                cansimmanager.src_id_from_canid(msg.arbitration_id) == self.gauge_id
                and cansimmanager.port_from_canid(msg.arbitration_id) == 0
                and msg.dlc == 1
                and cansimmanager.payload_byte(msg.data) == 1
            ):
                print(msg.data)
                break

    def test_buttons_manual_1(self):

        for msg in bus:
            if (
                cansimmanager.src_id_from_canid(msg.arbitration_id) == self.gauge_id
                and cansimmanager.port_from_canid(msg.arbitration_id) == 1
                and msg.dlc == 1
                and cansimmanager.payload_byte(msg.data) == 1
            ):
                print(msg.data)
                break


class Indicators1Tests(BaseGaugeTest):

    gauge_id = 27

    def test_alt_amp(self):
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(60))
        time.sleep(2)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(30))
        time.sleep(2)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(0))

    def test_oil_temp(self):
        self.send_command_2(port=1, payload=cansimmanager.make_payload_float(200))
        time.sleep(2)
        self.send_command_2(port=1, payload=cansimmanager.make_payload_float(100))
        time.sleep(2)
        self.send_command_2(port=1, payload=cansimmanager.make_payload_float(0))

    def test_oil_press(self):
        self.send_command_2(port=2, payload=cansimmanager.make_payload_float(90))
        time.sleep(2)
        self.send_command_2(port=2, payload=cansimmanager.make_payload_float(60))
        time.sleep(2)
        self.send_command_2(port=2, payload=cansimmanager.make_payload_float(0))

    def test_air_temp(self):
        self.send_command_2(port=3, payload=cansimmanager.make_payload_float(-10))
        time.sleep(2)
        self.send_command_2(port=3, payload=cansimmanager.make_payload_float(30))
        time.sleep(2)
        self.send_command_2(port=3, payload=cansimmanager.make_payload_float(0))


class Indicators2Tests(BaseGaugeTest):

    gauge_id = 25

    def test_fuel_1(self):
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(30))
        time.sleep(2)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(20))
        time.sleep(2)
        self.send_command_2(port=0, payload=cansimmanager.make_payload_float(0))

    def test_fuel_2(self):
        self.send_command_2(port=2, payload=cansimmanager.make_payload_float(30))
        time.sleep(2)
        self.send_command_2(port=2, payload=cansimmanager.make_payload_float(20))
        time.sleep(2)
        self.send_command_2(port=2, payload=cansimmanager.make_payload_float(0))

    def test_fuel_press(self):
        self.send_command_2(port=1, payload=cansimmanager.make_payload_float(50))
        time.sleep(2)
        self.send_command_2(port=1, payload=cansimmanager.make_payload_float(14))
        time.sleep(2)
        self.send_command_2(port=1, payload=cansimmanager.make_payload_float(0))


if __name__ == "__main__":
    unittest.main()
