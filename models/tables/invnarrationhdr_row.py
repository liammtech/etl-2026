from dataclasses import dataclass
from decimal import *
from datetime import date
from typing import Optional

# For pre-configured table row defaults, see /config/defaults/invnarrationhdr_defaults.yml

@dataclass
class InvNarrationHdrRow:
    StockCode: str
    TextType: Optional[str]
    DateLastModified: date