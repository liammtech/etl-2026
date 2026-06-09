import re
import tools.sql as sql


def check_if_d_code(stock_code: str) -> bool:
    '''
    - ends in a letter "D"
    - has a text prefix of a variable number of letters (TODO: factor in valid KK prefixes from config file)
    - between them, it contains three numeric characters
    '''
    return bool(
        re.fullmatch(r"[A-Za-z]+\d{3}D", stock_code)
    )


def check_if_non_d_code_exists(stock_code: str) -> bool:
    stock_code = stock_code[:-1]

    non_d_code = sql.get_single_record(
        table="InvMaster",
        criteria={
            "StockCode": stock_code
        }
    )

    return True if non_d_code else False