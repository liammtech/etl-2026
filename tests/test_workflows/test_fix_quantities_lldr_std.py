import pytest
from workflows.boms.fix_quantities import lldr_mdf_std_single
from tools.validation import RecordNotFoundError


def test_lldr_mdf_single():
    lldr_mdf_std_single(
        stock_code="JTEGLG001"
    )

