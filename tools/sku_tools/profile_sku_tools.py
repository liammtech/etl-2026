from validation.general_validation import check_if_customer

def generate_profile_stock_code(
    customer_code: str
) -> str:
    
    '''
    1. Check if customer code is in ArCustomers table
    2. If not, prompt the user that if they wish to continue, the profile will be [Customer code]/001 - do they wish to proceed?
        - If yes, concatenate the code and return it
    3. If the customer code is in the table, continue with code generation
    4. Check if the customer has taken any profiles before:
        - Query against InvMaster: AlternateKey2 = CustCode* 
    '''

    print(check_if_customer(customer_code=customer_code))