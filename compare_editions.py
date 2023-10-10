'''
Compares the master_database and current_database chart numbers in mathcing tables (tables = folders) and 
reports on:
1. charts withdrawn - charts that exist in the master_database but are not in the current_database.
2. new charts - charts that don't exist in the master_database but do exist in the current_database.

Note - either of the above conditions can also be considered errors on the CHS DVD which is why the user 
needs to accept the indicated reports before moving on and updating the master_database with the current_database.

'''

# Import necessary modules
import common_utils as utils

# Define the RunChecker class
class CompareEditions():

    # Constructor for initializing the CompareEditions object
    def __init__(self):

        print('compare editions')


# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
