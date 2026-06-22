from dataclasses import dataclass
from decimal import *
from typing import Optional

# For pre-configured table row defaults, see /config/defaults/invwarehouseplus_defaults.yml

@dataclass
class InvWarehousePlusRow:
    StockCode: str
    Warehouse: Optional[str] = None
    PickingRoute: Optional[str] = None