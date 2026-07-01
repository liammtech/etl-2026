import pytest
from workflows.bom_workflows.fix_quantities_multiple import lldr_std_range
from validation.general_validation import RecordNotFoundError

def test_lldr_range():
    lldr_std_range(
        stock_code="ORA*117"
    )

