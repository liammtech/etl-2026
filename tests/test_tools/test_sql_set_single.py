import pytest
from pyodbc import Row
from tools.sql import append_single_record, get_single_record


def test_return_type():
    append_single_record(
        table = "InvMaster",
        post_data = {
            "StockCode": "TESTCODE42"
        }  
    )

    return_val = get_single_record(
        table = "InvMaster",
        criteria = {
            "StockCode": "TESTCODE42"
        }  
    )

    print(return_val)
    assert type(return_val) == Row


