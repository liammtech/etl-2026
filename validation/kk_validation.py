import re
from pprint import pprint
import db.sql as sql
from config.loaders.kitchen_kit import get_kitchen_kit_values

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


def check_if_cab_config_has_any_drilled_doors(stock_code: str) -> bool:
    """
    Check if a particular Kitchen Kit cabinet configuration number (01, 02),
    should have any doors in it's BOM that need to be drilled.

    Args:
        stock_code: This can be a main range stock code, or just the final two
        characters. The function strips it down to the last two characters and
        checks if they're a valid key in the Kitchen Kit configurations list.

    Returns:
        A bool value: True if there are any doors with a non-null drilling
        instruction associated with that config, otherwise False
    """

    config_to_check = stock_code[-2:]
    cab_configs = get_kitchen_kit_values(value_group="cab-configs")

    frontals = cab_configs["kk_cab_configs"][config_to_check]["frontals"]

    frontal_drillings = []

    for i, j in enumerate(frontals):
        frontal_drillings.append(frontals[i]["drilling"])

    if any(drill_instance != 'None' for drill_instance in frontal_drillings):
        print(f"\nConfig {config_to_check} contains drilling: {frontal_drillings}")
        return True
    else:
        print(f"\nConfig {config_to_check} is an undrilled config")
        return False


def check_if_door_config_is_drilled(
        parent_code: str,
        door_code: str | None = None,
        door_size: str | None = None
    ) -> bool:
    """
    Check if a particular door within a particular Kitchen Kit cabinet config
    needs to be drilled. Works from the door size as a key (accepts either the
    door code from the BOM or the door size directly).

    Exactly one of door_code or door_size must be provided.

    TODO: Door size as a key could become ineffective if multiple sizes exist
    with different drilling patterns, within the same unit. At this point in
    time, there are no Kitchen Kit configs that have multiples of the same door
    with different drilling. This has not always been the case and could change
    at a later point, so work will need to be done to futureproof: a specific
    door id system.

    Args:
        parent_code: The parent code or config number you are looking to check
        within (parses the same as check_if_cab_config_has_any_drilled_doors() )

        door_code: Mutually exclusive with door_size. The code as it appears in
        the BOMs, looks up the size from it

        door_size: Mutually exclusive with door_size. Expected in "715X596"
        format, works directly as a key

    Returns:
        A bool value: True if the door is to be drilled, otherwise False
    """

    if (door_code is None) == (door_size is None):
        raise ValueError(
            "Exactly one of 'door_code' or 'door_size' must be provided."
        )
    
    if door_code is not None:
        door_height, door_width = sql.get_single_record(
            table="zInvExtra",
            criteria={
                "StockCode": door_code
            },
            return_columns={
                "Height",
                "Width"
            },
        )

        door_size = str(int(door_height)) + "X" + str(int(door_width))
        
    print(f"Door size is {door_size}")
    config_to_check = parent_code[-2:]
    cab_configs = get_kitchen_kit_values(value_group="cab-configs")

    drilling = next(
        (
            item["drilling"]
            for item in cab_configs["kk_cab_configs"][config_to_check]["frontals"]
            if item["size"] == door_size
        ),
        None
    )

    if drilling is not None:
        print(f"Door is drilled - drilling: {drilling}")
        return True
    else:
        print("Door is undrilled")
        return False
    

def check_if_standalone_door_is_drilled(
        door_sales_code: str,
        check_if_kk_door_sales: bool = False
    ):
    """
    Takes a simple Kitchen Kit door sales code (specifically a sales code), and determines if that door is supposed to be drilled or not

    Args:
        door_code: The sales code to check if it's to be drilled

    Returns:
        bool
    """

    if check_if_kk_door_sales:
        if not check_if_valid_kk_door_sales_code(stock_code=door_sales_code):
            print("Not a valid KK door sales code - terminating.")
            return
        
    sales_code_suffix = door_sales_code[6:]

    door_drillings = get_kitchen_kit_values("door-sizes")

    if door_drillings["kk_door_sizes"][sales_code_suffix]:
        return True
    else:
        return False