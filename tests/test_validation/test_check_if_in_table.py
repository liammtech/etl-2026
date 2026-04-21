from tools.sql import get_single_record, get_multiple_records
import validation.general_validation as general_validation

def test_single_code():
    result = general_validation.check_if_in_table(
        stock_code="SWCdfC012",
        table="InvMaster",
        sql_getter_func=get_single_record
    )