import pytest
from workflows.boms.fix_quantities import memp_std_single
from tools.validation import RecordNotFoundError


def test_bom_exists():
    memp_std_single(
        stock_code="SWCC012"
    )

