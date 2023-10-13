'''
new editions in column 3 either EDTN (Vector) or Edn Date (Raster)

process:
    confirm column 3 entry for each chart (row) matches; if yes no need to check anything else because no change to edition date/number
    if they don't match:
        raster: check the date of current is newer than master
            if yes = new edition
            if no = possible error
        vector: check if current edition number is greater that master edition number
            if yes = new edition
            if no = possible error

'''

# Import necessary modules
import common_utils as utils

# Define the RunChecker class
class FindDataMismatches():

    # Constructor for initializing the CompareEditions object
    def __init__(self):

        print('looking for mismatches')


# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
