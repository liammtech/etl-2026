from dataclasses import dataclass
from decimal import *
from datetime import date
from typing import Optional

# For pre-configured table row defaults, see /config/defaults/invwarehouse_defaults.yml

@dataclass
class InvWarehouseRow:
    StockCode: str
    Warehouse: Optional[str] = None
    DefaultBin: Optional[str] = None
    DateWhAdded: Optional[date] = None