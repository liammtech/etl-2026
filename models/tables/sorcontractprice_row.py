from dataclasses import dataclass
from decimal import *
from datetime import date
from typing import Optional

# For pre-configured table row defaults, see /config/defaults/sorcontractprice_defaults.yml

@dataclass
class SorContractPrice:
  CustomerBuyGrp: str
  StockCode: str
  Contract: Optional[str]
  StartDate: date
  ExpiryDate: date
  FixedUom: Optional[str]
  FixedPrice: Decimal