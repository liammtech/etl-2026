import pytest
from pyodbc import Row
from tools.sql import get_multiple_records


def test_return_type():
    return_val = get_multiple_records(
        table = "InvMaster",
        criteria = {
            "StockCode": "ORAGW*"
        },
        return_columns = [
            "StockCode",
            "Description",
            "LongDesc",
            "AlternateKey2",
            "ProductClass"
        ],
        order_by = "StockCode"
    )

    print(return_val)

    assert isinstance(return_val, list)
    if len(return_val) > 0:
        assert isinstance(return_val[0], Row)

'''
def test_without_return_columns():
    return_val = get_multiple_records(
        table = "InvMaster",
        criteria = {
            "StockCode": "ORAGW001"
        }  
    )

    # print(return_val)
    assert type(return_val) == Row
'''