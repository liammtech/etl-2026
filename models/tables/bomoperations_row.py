from dataclasses import dataclass
from decimal import *

# For pre-configured table row defaults, see /config/defaults/bomoperations_defaults.yml

@dataclass
class BomOperationsRow:
    StockCode: str
    Route: str
    Operation: int
    WorkCentre: str
    Milestone: str