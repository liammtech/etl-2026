import pytest
from workflows.boms.fix_quantities import memp_std_single
from tools.validation import RecordNotFoundError


def test_bom_exists():
    memp_std_single(
        stock_code="SWCC012"
    )

def test_bom_not_exists():
    with pytest.raises(RecordNotFoundError) as e_info:    
        memp_std_single(
            stock_code="BUNCHOFRUBBISH"
        )