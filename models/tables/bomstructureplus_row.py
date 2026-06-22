from dataclasses import dataclass
from decimal import *
from typing import Optional

# For pre-configured table row defaults, see /config/defaults/bomstructureplus_defaults.yml

@dataclass
class BomStructurePlusRow:
    ParentPart: str
    Route: str
    SequenceNo: str
    Component: str
    ComponentInstructi: Optional[str]