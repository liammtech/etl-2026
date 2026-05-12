from dataclasses import dataclass
from decimal import *
from typing import Optional

# For pre-configured table row defaults, see /config/defaults/porsupstkintr_defaults.yml

@dataclass
class PorSupStkInterRow:
    SupCatalogueNum: Optional[str]
    Supplier: Optional[str]
    StockCode: Optional[str]