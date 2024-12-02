import sqlite3
import pandas as pd

# Specify the path to your CSV file
csv_file_path = "Housing.csv"  # Replace with the path to your CSV file
db_file_path = "Database.db"    # Replace with the path to your desired SQLite database file

# Load the CSV into a Pandas DataFrame
df = pd.read_csv(csv_file_path)

# Connect to SQLite database (or create it if it doesn't exist)
connection = sqlite3.connect(db_file_path)

# Convert DataFrame to SQLite database table
table_name = "HOUSE"  # Name of the table to be created
df.to_sql(table_name, connection, if_exists="replace", index=False)

# Verify the data was inserted
print(f"Data from {csv_file_path} has been inserted into the database {db_file_path} in the table '{table_name}'.")
print("\nThe records in the table are:")

# Fetch and display all records
cursor = connection.cursor()
rows = cursor.execute(f"SELECT * FROM {table_name}").fetchall()
for row in rows:
    print(row)

# Commit changes and close connection
connection.commit()
connection.close()
