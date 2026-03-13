import pytest
from workflows.boms.fix_quantities_multiple import memp_std_range
from tools.validation import RecordNotFoundError

def test_bom_exists():
    memp_std_range(
        stock_code="FFPDMC%"
    )

