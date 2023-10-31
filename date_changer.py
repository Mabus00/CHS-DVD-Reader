''' 
created this program so i can change some dates to confirm checker is working properly

'''

import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('current_month.db')
cursor = conn.cursor()

# Define the new date value and the record to update
new_edtn = "1.000"
enc_id = 'CA473495'  # Assuming you want to update the record with ID 1
table_name = "EastDVD_20230825_V_CEN_B"  # Specify the table name

# Execute an SQL UPDATE statement for the specific table
update_sql = f"UPDATE {table_name} SET EDTN = ? WHERE ENC = ?"
cursor.execute(update_sql, (new_edtn, enc_id))

# Commit the changes and close the database connection
conn.commit()
conn.close()
