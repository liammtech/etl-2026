from dataclasses import dataclass
from decimal import *
from typing import Optional

# For pre-configured table row defaults, see /config/defaults/bomoperationsplus_defaults.yml

@dataclass
class BomOperationsPlusRow:
    StockCode: str
    Route: str
    Operation: int