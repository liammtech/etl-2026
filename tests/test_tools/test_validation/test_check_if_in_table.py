from tools.sql import get_single_record, get_multiple_records
import tools.validation as validation

def test_single_code():
    result = validation.check_if_in_table(
        stock_code="SWCdfC012",
        table="InvMaster",
        sql_getter_func=get_single_record
    )