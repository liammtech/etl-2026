import re
from pprint import pprint
import tools.sql as sql
from tools.config_tools.config_loader import get_kitchen_kit_values

def check_if_valid_main_range_KK_code(stock_code: str) -> bool:
    '''
    -x 8 characters long
    -x begins with 4 letters
    -x ends in 4 numbers
    -x letter one is either "F" or "R" (service key)
    -x letters 2 and 3 are in ["KK", "KG", "KU"] (cab colour key)
    -x letter 4 is in KK door range key
    -x first two numbers are in KK door colour key
    -x last two numbers are in KK config key
    - Will do product class as it's own validator - not applicable in every case (e.g. if code doesn't exist yet)
    '''
    
    stock_code = stock_code.upper().strip()

    reasons_not_valid = []

    # 8 Characters long
    if len(stock_code) != 8:
        reasons_not_valid.append("Not 8 characters long\n")

    # First 4 characters are alphabetical
    isalpha_matches = []

    for char in stock_code[:4]:
        isalpha_matches.append(char.isalpha())

    if False in isalpha_matches:
        reasons_not_valid.append("First 4 characters are not all alphabetical\n")

    # Last 4 characters are numeric
    isalpha_matches = []

    for char in stock_code[-4:]:
        isalpha_matches.append(char.isnumeric())

    if False in isalpha_matches:
        reasons_not_valid.append("Last 4 characters are not all numeric\n")

    # First letter is either "F" or "R" (service key)
    
    service_types = get_kitchen_kit_values(value_group="service-types")
    service_type_keys = list(service_types["kk_service_types"].keys())

    if stock_code[0] not in service_type_keys:
        reasons_not_valid.append("First character not a valid KK service type\n")

    # Letters 2 and 3 are in ["KK", "KG", "KU"] (cab colour key)
    cab_colours = get_kitchen_kit_values(value_group="cab-colours")
    cab_colour_keys = list(cab_colours["kk_cab_colours"].keys())

    if stock_code[1:3] not in cab_colour_keys:
        reasons_not_valid.append("Second + third character not a valid KK cab colour\n")

    # Letter 4 in valid door styles
    door_styles = get_kitchen_kit_values(value_group="door-styles")
    door_style_keys = list(door_styles["kk_door_styles"].keys())

    if stock_code[3] not in door_style_keys:
        reasons_not_valid.append("Fourth character not a valid KK door style\n")

    # Valid colour
    door_colours = get_kitchen_kit_values(value_group="door-colours")
    door_colour_keys = list(door_colours["kk_door_colours"].keys())

    if stock_code[4:6] not in door_colour_keys:
        reasons_not_valid.append("5th and 6th characters not a valid KK door colour\n")

    # Valid cab config
    cab_configs = get_kitchen_kit_values(value_group="cab-configs")
    cab_config_keys = list(cab_configs["kk_cab_configs"].keys())

    if stock_code[6:8] not in cab_config_keys:
        reasons_not_valid.append("7th and 8th characters not a valid KK cab config\n")

    if reasons_not_valid:
        message = (
            f"\n\n{stock_code} not a valid KK main range code - reasons listed:\n"
            + "".join(reasons_not_valid)
        )
        print(message)
        return False
    else:
        print(f"{stock_code} is a valid main range KK code")
        return True


def check_if_valid_kk_door_sales_code(stock_code: str) -> bool:
    '''
    - e.g. JKKD00715X596
    - e.g. OKKD30283X496A

    - Cannot validate by total length as it is variable x
    - Begins with 4 alphabetical characters x
    - First character in KK door styles keys x
    - Characters 2/3/4 are "KKD" x 
    - Characters 5 & 6 are in KK door colours keys x
    - From position 7 onwards, there are either 3 or 4 numeric characters
    - After that first numeric segment, there's an "X"
    - After the X, there are another 3 or 4 numeric characters
    - Optionally, ends in a single alphabetical character (usually not there, but is sometimes)
    '''

    stock_code = stock_code.upper().strip()

    reasons_not_valid = []

    # Begins with 4 alphabetical characters
    isalpha_matches = []

    for char in stock_code[:4]:
        isalpha_matches.append(char.isalpha())

    if False in isalpha_matches:
        reasons_not_valid.append("First 4 characters are not all alphabetical\n")

    # First character in KK door styles keys
    door_styles = get_kitchen_kit_values(value_group="door-styles")
    door_style_keys = list(door_styles["kk_door_styles"].keys())

    if stock_code[0] not in door_style_keys:
        reasons_not_valid.append("Fourth character not a valid KK door style\n")

    # Characters 2/3/4 are "KKD"
    if stock_code[1:4] != "KKD":
        reasons_not_valid.append("KKD substring not found\n")

    # Characters 5 & 6 are in KK door colours keys
    door_colours = get_kitchen_kit_values(value_group="door-colours")
    door_colour_keys = list(door_colours["kk_door_colours"].keys())

    if stock_code[4:6] not in door_colour_keys:
        reasons_not_valid.append("5th and 6th characters not a valid KK door colour\n") 

    # From position 7 onwards, there are either 3 or 4 numeric characters
    dimension_start = 6

    first_numeric_segment = ""

    for char in stock_code[dimension_start:]:
        if char.isdigit():
            first_numeric_segment += char
        else:
            break

    if len(first_numeric_segment) not in [3, 4]:
        reasons_not_valid.append("First dimension must be 3 or 4 numeric characters\n")

    next_index = dimension_start + len(first_numeric_segment)

    # After that first numeric segment, there's an "X"

    if next_index >= len(stock_code) or stock_code[next_index] != "X":
        reasons_not_valid.append("First dimension must be followed by X\n")

    next_index += 1

    # After the X, there are another 3 or 4 numeric characters

    second_numeric_segment = ""

    for char in stock_code[next_index:]:
        if char.isdigit():
            second_numeric_segment += char
        else:
            break

    if len(second_numeric_segment) not in [3, 4]:
        reasons_not_valid.append("Second dimension must be 3 or 4 numeric characters\n")

    next_index += len(second_numeric_segment)

    # Optionally, ends in a single alphabetical character (usually not there, but is sometimes)

    remaining = stock_code[next_index:]

    if remaining and not (len(remaining) == 1 and remaining.isalpha()):
        reasons_not_valid.append("Code may only end with one optional alphabetical character\n")

    if reasons_not_valid:
        message = (
            f"\n\n{stock_code} not a valid KK door sales code - reasons listed:\n"
            + "".join(reasons_not_valid)
        )
        print(message)
        return False
    else:
        print(f"{stock_code} is a valid KK door sales code")
        return True


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