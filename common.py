import struct
import can

# common code
def make_id(id_src, id_dst, priority, port) -> int:
    msg = 0
    # 4 bits: (25 .. 28) priority (0 .. 15)
    msg = msg | ((priority & 0b1111) << 25)
    # 5 bits: (20 .. 24) port
    msg = msg | ((port & 0b11111) << 20)
    # 10 bits (10 .. 19): dst address (0 .. 1023)
    msg = msg | ((id_dst & 0b1111111111) << 10)
    # 10 bits (0 .. 9): src address (0 .. 1023)
    msg = msg | ((id_src & 0b1111111111) << 0)
    return msg

def make_payload_float(num: float) -> list:
    return list(struct.pack("f", num))

def send_command(bus, id_src, id_dst, priority, port, payload):
    msg = can.Message(arbitration_id=make_id(id_src, id_dst, priority, port),
            data=payload, is_extended_id=True)
    bus.send(msg)
    