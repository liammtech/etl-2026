import pytest
from pyodbc import Row
from tools.sql import shift_unique_sequence, get_multiple_records


def test_posting():
    shift_unique_sequence(
        table="BomOperations",
        sequence_column="Operation",
        criteria={
            "StockCode": "FFPDMC001",
            "Route": "0"
        },
        delta=-1
    )

    return_val = get_multiple_records(
        table = "BomOperations",
        criteria = {
            "StockCode": "FFPDMC001"
        }  
    )

    print(return_val)