print(f'Invoking __main__.py for {__name__}')

from .common import *

if __name__ == "__main__":
    print("main script will be here in future")

    config = read_config()
    bus = can.interface.Bus(
        interface="slcan",
        channel=config["channel"],
        ttyBaudrate=config["ttyBaudrate"],
        bitrate=1000000,
    )

    # enable voltage
    send_command(bus, 1, 31, 0, 1, make_payload_byte(12))
    send_command(bus, 1, 31, 0, 2, make_payload_byte(1))

    bus.shutdown()