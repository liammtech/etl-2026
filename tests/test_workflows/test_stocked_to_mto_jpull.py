from workflows.bom_workflows.stocked_to_mto_jpull import switch_jpull_stocked_to_mto

def test_switch_to_mto():
    switch_jpull_stocked_to_mto(
        stock_code="PJMW895X296"
    )
        