import pytest
from pyodbc import Row
from db.sql import append_single_record, get_single_record


def test_return_type():
    append_single_record(
        table = "WipJobAllMat",
        row = {
            "Job": "000000009889888"
        }  
    )

