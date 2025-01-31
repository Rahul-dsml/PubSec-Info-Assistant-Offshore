import sqlite3
import pandas as pd
import os
import json
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
load_dotenv()



class ColumnDetail(BaseModel):
    col_id: int
    col_name: str
    col_type: str
    col_desc: str

class TableDetail(BaseModel):
    table_id: str
    table_name: str
    table_desc: str
    top_3: str
    columns: List[ColumnDetail]

class DataDictionaryPrompt:
    def __init__(self) -> None:
        """
        Initialize DataDictionaryPrompt with paths for the Excel file and SQLite database.

        Args:
            excel_file_path (Optional[str]): The path to the Excel file (default: environment variable EXCEL_FILE_PATH).
            sql_db (Optional[str]): The path to the SQLite database (default: environment variable DATABASE_PATH).
        """
        self.excel_file_path = os.getenv("EXCEL_FILE_PATH")
        self.sql_db =  os.getenv("DATABASE_PATH")

    def __get_data_dict(self) -> Optional[List[dict]]:
        """
        Retrieve the data dictionary from the Excel file and store it into an SQLite database.

        Returns:
            List[dict]: A list of dictionaries representing the columns in the data dictionary, or None if an error occurs.
        """
        try:
            # Load the Excel sheet into a pandas DataFrame
            df = pd.read_excel(self.excel_file_path)
            df = df.reset_index()
            df = df.rename(
                {"index": "col_id", "Field Name": "column_name", "Data Type": "col_dtype", "Description": "col_desc"},
                axis=1
            )
            # Create an in-memory SQLite database
            conn = sqlite3.connect(self.sql_db)
            # Load the DataFrame into the SQLite database
            df.to_sql("dict_data", conn, index=False, if_exists="replace")
            query = "SELECT * FROM dict_data"
            # Execute the SQL query
            df1 = pd.read_sql_query(query, conn)
            data_dict = df1.to_dict(orient="records")
            return data_dict  # Return the DataFrame with query results

        except Exception as e:
            print(f"SQL query didn't work due to: {e}")
            return None

        finally:
            # Close the database connection
            conn.close()

    def __get_top3(self) -> Optional[pd.DataFrame]:
        """
        Retrieve the top 3 rows from the real_estate table.

        Returns:
            pd.DataFrame: A DataFrame containing the top 3 rows from the real_estate table, or None if an error occurs.
        """
        try:
            # Load an SQLite database
            conn = sqlite3.connect(self.sql_db)
            query = "SELECT * FROM real_estate LIMIT 3"
            # Execute the SQL query
            top_df = pd.read_sql_query(query, conn)
            return top_df  # Return the DataFrame with query results

        except Exception as e:
            print(f"Data Dictionary Prompt :: SQL query didn't work due to: {e}")
            return None

        finally:
            # Close the database connection
            conn.close()

    def __get_table_details_with_columns(self) -> str:
        """
        Combine the table details and column details into a structured format.

        Returns:
            str: A JSON string containing the table details, column details, and top 3 rows from the real_estate table.
        """
        column_details = self.__get_data_dict()
        top_3 = self.__get_top3()

        # Initialize a structure to hold the combined result
        result = []
        table_id = "1"
        table_name = "real_estate"
        table_desc = """
        The real_estate table provides detailed information about real estate projects and units, including project details, location,
        pricing, availability, and construction status. It tracks unit-level attributes such as size, floor, number of bedrooms and bathrooms,
        and pricing details for beneficiaries and non-beneficiaries. The table also includes metadata like construction completion percentage,
        payment options, and platform accessibility (web/mobile).
        """

        print(f"Table Name: {table_name} ID: {table_id}")

        # Append the table details and its columns to the result
        result.append(
            TableDetail(
                table_id=table_id,
                table_name=table_name,
                table_desc=table_desc,
                top_3=top_3.to_csv(index=False),
                columns=[
                    ColumnDetail(
                        col_id=column["col_id"],
                        col_name=column["column_name"],
                        col_type=column['col_dtype'],
                        col_desc=column["col_desc"]
                    )
                    for column in column_details
                ]
            ).dict()
        )

        return json.dumps(result)

    def get_prompt(self) -> str:
        """
        Generate the prompt string for data dictionary.

        Returns:
            str: A formatted string that includes table and column details along with the top 3 rows from the real_estate table.
        """
        data_dictionary = self.__get_table_details_with_columns()
        data_dictionary_prompt = ''

        for table in json.loads(data_dictionary):
            data_dictionary_prompt += f"# Table Name: {table['table_name']}\n# Table Description: {table['table_desc']}\n"
            data_dictionary_prompt += "\n\n# Columns (with data type and description):\n"
            for column in table['columns']:
                data_dictionary_prompt += f"{column['col_name']} ({column['col_type']}): {column['col_desc']}\n"
            data_dictionary_prompt += f"\n/* \n3 rows from {table['table_name']} table:\n"
            data_dictionary_prompt += table['top_3']
            data_dictionary_prompt += "*/ \n\n"

        return data_dictionary_prompt
