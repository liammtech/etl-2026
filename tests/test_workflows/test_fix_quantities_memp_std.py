import pytest
from workflows.boms.fix_quantities import memp_std


def test_bom_exists():
    memp_std(
        stock_code="SWCC012"
    )

# def test_bom_not_exists():
#     with pytest.raises(Exception) as e_info:    
#         memp_std(
#             stock_code="BUNCHOFRUBBISH"
#         )