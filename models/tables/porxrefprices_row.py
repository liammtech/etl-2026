from dataclasses import dataclass
from decimal import *
from datetime import date
from typing import Optional

# For pre-configured table row defaults, see /config/defaults/porxrefprices_defaults.yml

@dataclass
class PorXrefPrices:
    Supplier: str
    StockCode: str
    Contract: str
    PriceUom: Optional[str]
    PriceStartDate: Optional[date]
    PriceExpiryDate: Optional[date]
    MinimumQtyUom: Optional[str]