from dataclasses import dataclass
from decimal import *
from typing import Optional

# For pre-configured table row defaults, see /config/defaults/bomstructure_defaults.yml

@dataclass
class BomStructureRow:
    ParentPart: str
    Route: str
    SequenceNo: str
    Component: str
    OperationOffset: int
    QtyPer: Optional[Decimal]
    ScrapPercentage: Optional[Decimal]
    InclKitIssues: Optional[str]
    CreateSubJob: Optional[str]
    UomFlag: Optional[str]
    QtyPerEnt: Optional[Decimal]