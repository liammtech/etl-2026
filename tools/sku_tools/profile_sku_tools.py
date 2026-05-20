from validation.general_validation import check_if_customer

def generate_profile_stock_code(
    customer_code: str
) -> str:
    print(check_if_customer(customer_code=customer_code))