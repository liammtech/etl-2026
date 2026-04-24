from tools.bom_tools.bom_organisation import get_next_op_number

def test_get_next_op_number():
    next_op = get_next_op_number(
        stock_code="PJMW046",
        route=0
    )
    print(next_op)