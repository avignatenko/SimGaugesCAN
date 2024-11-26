import json
import locale
import os
import struct

import can


# common code
def make_id(id_src, id_dst, priority, port) -> int:
    msg = 0
    # 4 bits: (25 .. 28) priority (0 .. 15)
    msg |= (priority & 15) << 25
    # 5 bits: (20 .. 24) port
    msg |= (port & 31) << 20
    # 10 bits (10 .. 19): dst address (0 .. 1023)
    msg |= (id_dst & 1023) << 10
    # 10 bits (0 .. 9): src address (0 .. 1023)
    return msg | ((id_src & 0b1111111111) << 0)


def src_id_from_canid(canid: int) -> int:
    return canid & 0b1111111111


def port_from_canid(canid: int) -> int:
    return (canid >> 20) & 0b11111


def payload_byte(data) -> int:
    return data[0]


def payload_ushort(data) -> int:
    return struct.unpack("<H", data)[0]


def payload_float(data) -> float:
    return struct.unpack("<f", data)[0]


def make_payload_float(num: float) -> list:
    return list(struct.pack("f", num))


def make_payload_byte(num: int) -> list:
    return list(struct.pack("B", num))


def make_message(id_src, id_dst, priority, port, payload):
    return can.Message(
        arbitration_id=make_id(id_src, id_dst, priority, port),
        data=payload,
        is_extended_id=True,
    )


def send_command(bus, id_src, id_dst, priority, port, payload):
    msg = make_message(id_src, id_dst, priority, port, payload)
    bus.send(msg)


def read_config(folder="."):
    with open(os.path.join(folder, "config.json"), encoding=locale.getpreferredencoding(False)) as file:
        return json.load(file)
