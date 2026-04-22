import pytest
from pyodbc import Row
from tools.sql import get_single_record


# def test_return_type():
#     return_val = get_single_record(
#         table = "InvMaster",
#         criteria = {
#             "StockCode": "ORAGW001"
#         },
#         return_columns = [
#             "StockCode",
#             "Description",
#             "LongDesc",
#             "AlternateKey2",
#             "ProductClass"
#         ]    
#     )

#     # print(return_val)
#     assert type(return_val) == Row


# def test_without_return_columns():
#     return_val = get_single_record(
#         table = "InvMaster",
#         criteria = {
#             "StockCode": "ORAGW001"
#         }  
#     )

#     # print(return_val)
#     assert type(return_val) == Row

def test_with_return_column_as_string():
    rtn = get_single_record(
        table="zInvExtra",
        criteria={
            "StockCode": "PJMW895X296"
        },
        return_columns="LinkedStockCode",
        flatten=True
    )
    print(rtn)