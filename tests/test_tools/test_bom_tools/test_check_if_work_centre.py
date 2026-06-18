from tools.bom_tools.bom_organisation import check_if_work_centre_in_routing

def test_check():
    result = check_if_work_centre_in_routing(
        stock_code="PJMW895X296",
        route="5",
        work_centre="DJDET"
    )

    print(result)