from dataclasses import dataclass
from decimal import *
from typing import Optional

# For pre-configured table row defaults, see /config/defaults/invnarration_defaults.yml

@dataclass
class InvNarrationRow:
    StockCode: str
    TextType: Optional[str]
    Line: Optional[str]
    Text: Optional[str]