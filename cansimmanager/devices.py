import can


class Device:
    async def handle_can_message(self, message: can.Message, sim) -> None:
        return

    async def handle_updated_dataref(self, dataref:str, bus: can.Bus) -> None:
        return


class Devices:

    _devices_by_can_id: dict[int, list[Device]] = {}
    _devices_by_dataref: dict[str, list[Device]] = {}

    def register_device(self, device: Device, can_ids: list[int], datarefs: list[str]):
        for can_id in can_ids:
            self._devices_by_can_id.setdefault(can_id, []).append(device)
        for dataref in datarefs:
            self._devices_by_dataref.setdefault(dataref, []).append(device)

    def get_from_cansim_id(self, cansim_id: int) -> list[Device]:
        return self._devices_by_can_id.get(cansim_id)

    def get_from_dataref(self, dataref) -> list[Device]:
        return self._devices_by_dataref.get(dataref)

    def get_datarefs(self) -> list[str]:
        return self._devices_by_dataref.keys()