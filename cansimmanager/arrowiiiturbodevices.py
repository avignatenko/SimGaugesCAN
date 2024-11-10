
from .devices import Devices, Device

    

class GyroSuction(Device):
    pass



def register(devices: Devices):
    devices.register_device(device=GyroSuction(), can_ids=[29], datarefs=["a"])