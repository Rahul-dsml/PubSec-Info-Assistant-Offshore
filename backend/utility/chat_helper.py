import sqlite3
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import json

# Convert CSV to SQLite Database
def csv_to_sqlite(csv_file_path, sqlite_db_path):
    # Load CSV into pandas DataFrame
    df = pd.read_csv(csv_file_path, encoding='utf-8')
    # df = pd.read_csv()
    # Create SQLite database and write the DataFrame to it
    conn = sqlite3.connect(sqlite_db_path)
    df.to_sql('real_estate', conn, if_exists='replace', index=False)
#     return con


class DataDictionaryPrompt():

    def __init__(self,) -> None:
        # self.file_path=st.secrets.file.file_path or os.getenv('file_path')
        # self.sheet_name=st.secrets.file.sheet_name or os.getenv('sheet_name')
        self.dict_file_path="Data_Dictionary_v2.xlsx"
        
    def __get_data_dict(self):
        try:
            # Load the Excel sheet into a pandas DataFrame
            df = pd.read_excel(self.dict_file_path)
            df=df.reset_index()
            df=df.rename({"index":"col_id","Field Name":"column_name","Data Type":"col_dtype","Description":"col_desc"},axis=1)
            # Create an in-memory SQLite database
            # conn = sqlite3.connect(":memory:")
            conn = sqlite3.connect("real_estate.db")

            # Load the DataFrame into the SQLite database
            df.to_sql("dict_data", conn, index=False, if_exists="replace")
            
            query="select * from dict_data"

            # Execute the SQL query
            df1 = pd.read_sql_query(query, conn)
            data_dict=df1.to_dict(orient="records")
            return data_dict  # Return the DataFrame with query results
            
        except Exception as e:
            print("SQL query didn't work due to:", e)
            return None
        finally:
            # Close the database connection
            conn.close()

    def __get_top3(self):
        try:
            # Load an SQLite database
            conn = sqlite3.connect("real_estate.db")
            
            query="""select * from real_estate limit 3"""

            # Execute the SQL query
            top_df = pd.read_sql_query(query, conn)
           

            return top_df  # Return the DataFrame with query results

        except Exception as e:
            print("Data Dictionary Prompt :: SQL query didn't work due to:", e)
            return None
        finally:
            # Close the database connection
            conn.close()

    def __get_table_details_with_columns(self):
        column_details=self.__get_data_dict()
        top_3=self.__get_top3()
        # Initialize a structure to hold the combined result
        result = []
        table_id = "1"
        table_name="real_estate"
        table_desc="""The real_estate table provides detailed information about real estate projects and units, including project details, location, pricing, availability, and construction status. It tracks unit-level attributes such as size, floor, number of bedrooms and bathrooms, and pricing details for beneficiaries and non-beneficiaries. The table also includes metadata like construction completion percentage, payment options, and platform accessibility (web/mobile)."""
        print("Table Name ::", table_name ,"ID ::",table_id)
        # Append the table details and its columns to the result
        result.append({
            "table_id": table_id,
            "table_name":table_name,
            "table_desc": table_desc,
            "top-3":top_3.to_csv(index=False),
            "columns": [
                {
                    "col_id": column["col_id"],
                    "col_name": column["column_name"],
                    "col_type": column['col_dtype'],
                    "col_desc": column["col_desc"]
                }
                for column in column_details
            ]
        })
        
        return json.dumps(result)

    def get_prompt(self):
        data_dictionary=self.__get_table_details_with_columns()
        data_dictionary_prompt = ''
        for table in json.loads(data_dictionary):
            data_dictionary_prompt += f"# Table Name:{table['table_name']}\n# Table Description:{table['table_desc']}"
            data_dictionary_prompt += "\n\n# Columns(with data type and description):\n"
            for column in table['columns']:
                data_dictionary_prompt += f"{column['col_name']} ({column['col_type']}) : {column['col_desc']}\n"
            data_dictionary_prompt += f"""\n/* \n3 rows from {table['table_name']} table:\n"""
            data_dictionary_prompt+=table['top-3']
            data_dictionary_prompt += "*/ \n\n"
        return data_dictionary_prompt