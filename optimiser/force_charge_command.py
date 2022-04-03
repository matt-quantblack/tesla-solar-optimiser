from __future__ import annotations
import datetime
from typing import ClassVar, Optional
from optimiser.local_json_dataclass import LocalJsonDataclass


class ForceChargeCommand(LocalJsonDataclass):
    """
    The configuration for forcing the vehicle to charge

    Args:
        request_time: The time the force charge started
        force_charge: Set to True to immediately start charging the car
        min_vehcile_charge: The vehicle charge level that will initiate a force charge
        force_charge_level: The vehicle charge level that will stop force charging
        force_charge_amps: The power to use during the force charge
        min_spare_capacity: The minimum spare capacity in solar generation to attempt to turn charging on
        file_path: The path to save the json datafile
    """
    request_time: Optional[datetime.datetime] = None
    force_charge: bool = False
    min_vehicle_charge: int = 50
    force_charge_level: int = 70
    force_charge_amps: int = 5
    min_spare_capacity: int = 1250
    file_path: ClassVar[str] = 'force_charge.json'

    def is_forcing_charge(self, vehicle_charge: float) -> bool:
        return self.request_time is not None and vehicle_charge < self.force_charge_level
