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
class CompareChartNumbers():

    # Constructor for initializing the RunChecker object
    def __init__(self, master_database_cursor, current_database_cursor):

        # Establish database cursors
        self.master_database_cursor = master_database_cursor
        self.current_database_cursor = current_database_cursor

    def compare_chart_numbers(self, tables_master, master_yyyymmdd, current_yyyymmdd):

        print('compare tables')

        charts_withdrawn_result = []
        new_charts_result = []

        # Iterate through table names in tables_master and find corresponding table in tables_current_temp
        for table_name in tables_master:
            # add the yyyymmdd to match complete table name
            temp_master_table_name = utils.insert_text(table_name, master_yyyymmdd, pos_to_insert=1)
            temp_current_table_name = utils.insert_text(table_name, current_yyyymmdd, pos_to_insert=1)
            
            # Table exists in both databases; compare content
            self.master_database_cursor.execute(f"SELECT * FROM {temp_master_table_name}")
            master_data = self.master_database_cursor.fetchall()

            self.current_database_cursor.execute(f"SELECT * FROM {temp_current_table_name}")
            current_data = self.current_database_cursor.fetchall()

            # Set the index of the table column (first column = chart number)
            chart_column_index = 1

            # Create a set of chart numbers from current_data for faster lookup
            current_chart_numbers = set(row[chart_column_index] for row in current_data)

            # Initialize a list to new charts and store missing chart numbers
            new_charts = []
            missing_charts = []

            # Initialize a set to keep track of encountered chart names
            encountered_chart_numbers = set()

            # Iterate through rows of master_data and find missing chart numbers
            for i, row in enumerate(master_data):

                # get master_data chart name for the current row; remember the master is master!
                master_chart_number = row[chart_column_index]

                # Check if the chart name from master_data is in current_data; if not add to missing_charts list
                if (master_chart_number not in current_chart_numbers) and (master_chart_number not in encountered_chart_numbers):
                    # Append the missing chart name to the list
                    missing_charts.append(master_chart_number)
                
                # whether or not above condition fails add it to encountered_chart_numbers so we don't keep checking repeating master_chart_numbers
                if master_chart_number not in encountered_chart_numbers:
                    # Add the chart name to the encountered_chart_names set
                    encountered_chart_numbers.add(master_chart_number)

            # If there are missing charts for this table, add the table name and missing charts to the charts_withdrawn_result
            if missing_charts:
                charts_withdrawn_result.append((temp_current_table_name, missing_charts))
            


            # Create a set of chart numbers from current_data for faster lookup
            master_chart_numbers = set(row[chart_column_index] for row in master_data)

            # reset encountered chart names
            encountered_chart_numbers = set()

            # Iterate through rows of current_data and find new chart numbers
            for i, row in enumerate(current_data):

                # get master_data chart name for the current row; remember the master is master!
                current_chart_number = row[chart_column_index]

                # Check if the chart name from master_data is in current_data; if not add to missing_charts list
                if (current_chart_number not in master_chart_numbers) and (current_chart_number not in encountered_chart_numbers):
                    # Append the missing chart name to the list
                    new_charts.append(current_chart_number)
                
                # whether or not above condition fails add it to encountered_chart_numbers so we don't keep checking repeating master_chart_numbers
                if current_chart_number not in encountered_chart_numbers:
                    # Add the chart name to the encountered_chart_names set
                    encountered_chart_numbers.add(current_chart_number)

            # If there are new charts for this table, add the table name and new charts to the new_charts_result
            if new_charts:
                new_charts_result.append((temp_current_table_name, new_charts))

        return charts_withdrawn_result, new_charts_result
                
        # 3. start with master and find the same table (with the newer date) in current
        # self.compare_database_content()
        # 4. for each row compare: chart number, Edn Date, Last NM, Ed number and Title and report any discrepancies/ store them in a local table. Chart numbers matching will be a challenge if not the same.
        # 5. report all discrepancies (for now) as errors so you can see what the differences are.
        # 6. as you move forward and you can differentiate between new charts, new editions, and withdrawn charts, add these details to each specific local table, with the remainder staying in errors.


# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
