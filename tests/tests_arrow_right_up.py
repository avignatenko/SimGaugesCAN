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


class FuelSwitchTest(BaseGaugeTest):

    gauge_id = 30

    def test_fuel_switch_manual(self):

        for msg in bus:
            if cs.src_id_from_canid(msg.arbitration_id) == self.gauge_id:
                print(msg.data)
                break


class ButtonSwitchTest(BaseGaugeTest):

    gauge_id = 24

    def test_buttons_manual(self):

        ports_received = []
        for msg in bus:
            port = cs.port_from_canid(msg.arbitration_id)
            if cs.src_id_from_canid(msg.arbitration_id) == self.gauge_id:
                print(port)
                print(msg.data)
                if port not in ports_received:
                    ports_received.append(port)
                    print(f"Total: {len(ports_received)}")
                if len(ports_received) == 7:
                    break


class TransponderTest(BaseGaugeTest):

    gauge_id = 31

    def test_buttons_squawk_manual(self):

        # enable voltage
        self.send_command_2(port=1, payload=cs.make_payload_byte(12))

        for msg in bus:
            port = cs.port_from_canid(msg.arbitration_id)
            if (
                cs.src_id_from_canid(msg.arbitration_id) == self.gauge_id
                and port == 1
                and msg.dlc == 2
            ):
                print(msg.data)
                squawk = int.from_bytes(msg.data, byteorder="little")
                if squawk == 6666:
                    break

    def test_buttons_selector_manual(self):

        for msg in bus:
            port = cs.port_from_canid(msg.arbitration_id)
            if (
                cs.src_id_from_canid(msg.arbitration_id) == self.gauge_id
                and port == 0
                and msg.dlc == 1
            ):
                print(msg.data)
                break

    def test_button(self):
        # enable voltage
        self.send_command_2(port=1, payload=cs.make_payload_byte(12))

        for msg in bus:
            port = cs.port_from_canid(msg.arbitration_id)
            if (
                cs.src_id_from_canid(msg.arbitration_id) == self.gauge_id
                and port == 2
                and msg.dlc == 1
            ):
                print(msg.data)
                break

    def test_led(self):
        # enable voltage
        self.send_command_2(port=1, payload=cs.make_payload_byte(12))
        # send led 0
        self.send_command_2(port=2, payload=cs.make_payload_byte(0))
        time.sleep(1)
        self.send_command_2(port=2, payload=cs.make_payload_byte(1))
        time.sleep(1)
        self.send_command_2(port=2, payload=cs.make_payload_byte(0))
        # disable voltage
        self.send_command_2(port=1, payload=cs.make_payload_byte(0))


if __name__ == "__main__":
    unittest.main()
