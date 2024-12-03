# Load all the environment variables
from dotenv import load_dotenv
load_dotenv()

# Import necessary libraries
import streamlit as st
import os
import sqlite3
import pandas as pd
import google.generativeai as genai
from prompt import  *

# API Key for Gemini Model
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Function to get Gemini response (SQL query)
def get_gemini_response(question, prompt, table_name):
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash-8b")
        # Replace table name dynamically in the prompt
        updated_prompt = prompt.format(table_name, table_name, table_name, table_name)
        response = model.generate_content([updated_prompt, question])
        sql_query = response.candidates[0].content.parts[0].text.strip()
        return sql_query
    except Exception as e:
        st.error(f"Error fetching response: {e}")
        return None

# Function to convert CSV to SQLite database with dynamic table creation
def csv_to_sqlite(csv_file, db_path, table_name):
    try:
        # Load CSV into a DataFrame
        df = pd.read_csv(csv_file)

        # Check if DataFrame is empty
        if df.empty:
            st.error("CSV file is empty.")
            return

        # Connect to SQLite database
        connection = sqlite3.connect(db_path)

        # Write DataFrame to SQLite table (if table exists, replace it)
        df.to_sql(table_name, connection, if_exists="replace", index=False)

        # Close connection
        connection.close()

        # Success message
        st.success(f"CSV file '{csv_file.name}' has been successfully converted to the database '{db_path}' in the table '{table_name}'.")
    except Exception as e:
        st.error(f"Error converting CSV to database: {e}")

# Function to retrieve query(records) from the database
def read_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)  # Create connection with the database
        cur = conn.cursor()         # Cursor to execute SQL queries
        cur.execute(sql)            # Run the SQL query
        rows = cur.fetchall()       # Fetch all records
        conn.close()                # Close the connection
        return rows
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return []

# Define the Prompt (SQL query generation instructions)
prompt = PROMPT

# Streamlit UI setup
st.set_page_config(page_title="Retrieve SQL Data")
st.header("Retrieve SQL Data")

# File uploader for CSV file
st.subheader("Upload CSV to Convert to Database")
csv_file = st.file_uploader("Upload your CSV file:", type=["csv"])

# Specify table and database names
table_name = st.text_input("Enter table name:",placeholder="STUDENT")
db_name = st.text_input("Enter database name:", placeholder="student.db")

# If CSV file is uploaded and convert button is pressed
if csv_file and st.button("Convert CSV to Database"):
    csv_to_sqlite(csv_file, db_name, table_name)

# Query input and execution
st.subheader("Query the Database")
question = st.text_input("Input your question:", key="input")
submit = st.button("Ask the Question")

# If submit button is clicked
if submit:
    try:
        # Step 1: Get SQL Query from Gemini Model
        response = get_gemini_response(question, prompt, table_name)
        if response:
            st.write("Generated SQL Query:", response)

            # Step 2: Retrieve data from the database
            data = read_sql_query(response, db_name)

            # Step 3: Display results
            st.subheader("Database Response:")
            if data:
                for row in data:
                    st.write(row)
            else:
                st.write("No data returned from the query.")
        else:
            st.write("No response generated by Gemini.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
