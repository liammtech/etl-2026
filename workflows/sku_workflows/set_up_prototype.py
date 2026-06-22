import db.sql as sql

'''
This script is to allow the user to set up a new prototype code, when the need arises.
To begin with, it will focus on membrane pressed samples, which make up a significant majority of sample requests.

Later, sibling scripts/functions will be added to handle other types (JAYL, LLDR, PRWS).

All prototype codes are numbered from 01 to 100: one hundred codes per sample type, that are populated sequentially,
then begin to be reused after the latest sample reaches code 99, starting again at 01

It needs to be able to:
- Accept the user information required for the new sample request
- Validate the type of sample
- Identify the next sample code number to be used, checking:
    - Which was the last code to be used
    - IMPORTANT: check that the code it selects isn't due to be used in any current outstanding WIP
- Needs to then apply the relevant data to the existing code
'''

'''
MEMP-PTYPE:
1. The function will not take an argument at terminal - instead, you "enter into" a series of user prompts to accept the data

2. Upon engaging, the script first needs to determine which MEMP-PTYPE code is the next in sequence to be used:
    - As they have been used manually, the InvMaster.DateStkAdded date field has been updated to the current date, when each new sample is set up
    - As such, the highest date in this column amongst the MEMP-PTYPE* codes will dictate the last code that was used
    - The next code along becomes the candidate for the new code
    - The script then needs to check if this "candidate" code is present in any outstanding jobs: it checks for any WipMaster records that contain
    the candidate code in WipMaster.StockCode, while the record's WipMaster.Complete field is not set to "Y"
    - If there are no outstanding WIP records, the candidate code is confirmed
    - If there are outstanding WIP records, it picks the next code along: the process is repeated until the first code with no WIP is selected

3. Need to come up with a system for data-required - it is very case dependent on the type of BoM
    - will probably need to model the different BOM types first

'''