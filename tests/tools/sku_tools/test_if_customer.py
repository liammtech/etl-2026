from domain.sku.code_generation import generate_profile_stock_code

def test_profile_stock_code_calculation():
    generate_profile_stock_code(customer_code="B0167")
