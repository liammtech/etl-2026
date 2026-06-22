from dataclasses import dataclass
from decimal import *
from typing import Optional

# For pre-configured table row defaults, see /config/defaults/porsupstkinfo_defaults.yml

@dataclass
class PorSupStkInfoRow:
    Supplier: Optional[str]
    StockCode: str
    SupCatalogueNum: Optional[str]
    OrderQtyUom: Optional[str]
    LastPrcUom: Optional[str]