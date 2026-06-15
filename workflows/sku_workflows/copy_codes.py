def copy_oem_door_code_basic():
    '''
    This one will differ from the others a bit, it will work from user prompts rather than arguments

    PRELIMINARY
    1. Enter code to copy:
    2. Grab headline info for code and print it, include a message saying that it will maintain BOM et, just change size
    3. Enter code to copy to:
        - Do check that new code doesn't already exist, re-prompt if it does
    4. Enter new height + enter new width
    5. Enter new x-link (leave blank = puts the code itself there)
    6. Enter new price (leave blank = 999)

        - This script isn't going to do any fancy checking/validation etc, it is just copying the BOM and re-arranging the values as per
        - It is assumed that this is for like-for-like codes
        - The only thing that it may change is the pallet, depending on the size (need to finish palletiser functions)
        - Things like description/product type overrides will come later, either as flags or as part of a separate function

    VALIDATION
    - Determine code type: pressed, edged-mdf, edged-mfc, j-pull, 5-piece shaker

    PROCESS
    1. Copy the InvMaster data
    2. Copy the zInvExtra data
    3. Create fresh InvMaster record
        
    '''