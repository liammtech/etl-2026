import pytest
from workflows.bom_workflows.fix_quantities import lldr_std_single
from validation.general_validation import RecordNotFoundError

def test_lldr_single():
    lldr_std_single(
        stock_code="ORAG*117"
    )

