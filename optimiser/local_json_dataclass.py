from __future__ import annotations
from pathlib import Path
import json
from typing import ClassVar, TYPE_CHECKING, Any
if TYPE_CHECKING:  # Avoids circular references for type hints
    from optimiser.force_charge_command import ForceChargeCommand
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class LocalJsonDataclass:
    """
    Wraps a dataclass to enable save and load to a json file

    Args:
        file_path: The poth of the file to save the data
    """

    file_path: ClassVar[str] = 'data.json'

    def save(self):
        Path(self.file_path).write_text(json.dumps(self.to_json()))

    @classmethod
    def load(cls) -> Any:
        return cls.from_json(Path(cls.file_path).read_text())