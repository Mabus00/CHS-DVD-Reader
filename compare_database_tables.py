'''

'''

# Import necessary modules
import common_utils as utils

# Define the RunChecker class
class CompareDatabaseTables():

    # Constructor for initializing the RunChecker object
    def __init__(self, run_checker_textbox, new_charts_textbox, charts_withdrawn_textbox, errors_textbox, master_database_cursor, current_database_cursor):
        # Create an instance of CreateDatabaseSignals (not shown in code, assuming it's an imported class)
        self.run_checker_textbox = run_checker_textbox
        self.new_charts_textbox = new_charts_textbox
        self.chart_withdrawn_textbox = charts_withdrawn_textbox
        self.errors_textbox = errors_textbox

        # Establish database cursors
        self.master_database_cursor = master_database_cursor
        self.current_database_cursor = current_database_cursor

        self.master_yyyymmdd = ''
        self.current_yyyymmdd = ''

    def compare_database_tables(self, tables_master_temp, tables_current_temp, tables_missing_in_master, tables_missing_in_current, master_yyyymmdd, current_yyyymmdd):
        # tables_missing_in_current represent tables that have been newly deleted or a CHS error
        # tables_missing_in_master represent tables that have been newly added or a CHS error
        # either way it's been noted on the error tab so no need to take further action
        print('compare tables')
   
        # Remove tables_missing_from_current from tables_master so table content matches can occur
        tables_master_temp = [table for table in tables_master_temp if table not in tables_missing_in_current]

        # Iterate through table names in tables_master_temp and find corresponding table in tables_current_temp
        for table_name in tables_master_temp:
            # add the yyyymmdd to match complete table name
            temp_master_table_name = utils.insert_text(table_name, master_yyyymmdd, pos_to_insert=1)
            temp_current_table_name = utils.insert_text(table_name, current_yyyymmdd, pos_to_insert=1)
            
            # Table exists in both databases; compare content
            self.master_database_cursor.execute(f"SELECT * FROM {temp_master_table_name}")
            master_data = self.master_database_cursor.fetchall()

            self.current_database_cursor.execute(f"SELECT * FROM {temp_current_table_name}")
            current_data = self.current_database_cursor.fetchall()

            # Set the index of the "chart" column (first column = chart number)
            chart_column_index = 0

            # Create a set of chart names from current_data for faster lookup
            current_chart_numbers = set(row[chart_column_index] for row in current_data)

            # Initialize a list to store missing chart names
            missing_charts = []

            # Initialize a set to keep track of encountered chart names
            encountered_chart_numbers = set()

            # Iterate through rows of master_data
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


            # Print missing charts for the current row if any
            if missing_charts:
                self.chart_withdrawn_textbox.emit(f"Charts missing in current DVD folder {temp_current_table_name}:")
                # Concatenate the missing chart names with commas and print them
                missing_chart_str = ', '.join(missing_charts)
                self.chart_withdrawn_textbox.emit(missing_chart_str + '\n')
                

                
        # 3. start with master and find the same table (with the newer date) in current
        # self.compare_database_content()
        # 4. for each row compare: chart number, Edn Date, Last NM, Ed number and Title and report any discrepancies/ store them in a local table. Chart numbers matching will be a challenge if not the same.
        # 5. report all discrepancies (for now) as errors so you can see what the differences are.
        # 6. as you move forward and you can differentiate between new charts, new editions, and withdrawn charts, add these details to each specific local table, with the remainder staying in errors.


# Main execution block (can be used for testing)
if __name__ == "__main__":
    pass
