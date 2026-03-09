import pytest
from pyodbc import Row
from tools.sql import append_multiple_records, get_multiple_records


def test_return_type():
    append_multiple_records(

    )

    return_val = get_multiple_records(

    )

    print(return_val)

    assert isinstance(return_val, list)
    if len(return_val) > 0:
        assert isinstance(return_val[0], Row)

