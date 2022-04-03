from __future__ import annotations
import datetime
import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Optional
from dataclasses_json import dataclass_json
if TYPE_CHECKING:  # Avoids circular references for type hints
    from optimiser.force_charge_command import ForceChargeCommand


@dataclass_json
@dataclass
class ForceChargeCommand:
    request_time: Optional[datetime.datetime] = None
    force_charge: bool = False
    min_vehicle_charge: int = 50
    force_charge_level: int = 70
    force_charge_amps: int = 5
    min_spare_capacity: int = 1250

    def is_forcing_charge(self, vehicle_charge: float) -> bool:
        return self.request_time is not None and vehicle_charge < self.force_charge_level

    def save(self):
        Path('force_charge.json').write_text(json.dumps(self.to_json()))

    @staticmethod
    def load() -> ForceChargeCommand:
        return ForceChargeCommand.from_json(Path('force_charge.json').read_text())

