import pytest
from workflows.bom_workflows.fix_quantities import memp_std_single
from tools.validation import RecordNotFoundError


def test_bom_quantity_fix():
    memp_std_single(
        stock_code="MEMP-PTYPE78"
    )

