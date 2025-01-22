import sqlite3
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import json
from dotenv import load_dotenv
import os
load_dotenv()


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
        self.sqllite_db_path=r"C:\Users\rahul\Desktop\Offshore\PubSec-Info-Assistant-Offshore\backend\real_estate.db"
        # self.sqllite_db_path= os.getenv("DB_PATH")
       
    def __get_data_dict(self):
        try:
            # Load the Excel sheet into a pandas DataFrame
            df = pd.read_excel(r"C:\Users\rahul\Desktop\Offshore\PubSec-Info-Assistant-Offshore\backend\Data_Dictionary_v3.xlsx",sheet_name="dict2")
            # df = pd.read_excel(f"{os.getenv("DATA_PATH")}", sheet_name=os.getenv("SHEET_NAME")))
            # print(df)
            # Create an in-memory SQLite database
            conn = sqlite3.connect(self.sqllite_db_path)

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

    def __get_top3(self,table_name):
        try:
            # Load an SQLite database
            conn = sqlite3.connect(self.sqllite_db_path)
            
            query=f"""select * from {table_name} Limit 3"""

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
        
        # Initialize a structure to hold the combined result
        table_details={1:{"table_name":"project_details","table_desc":"""The `Project_Details` table provides project-level information, including project identifiers, location details (city, region, latitude, longitude), construction status, pricing information for Sakani and non-Sakani beneficiaries, and available payment options. It also captures minimum and maximum ranges for unit dimensions and features within the project.""" },
        2:{"table_name":"unit_details","table_desc":"""The Unit_Details table contains information about individual apartment units within real estate projects, including attributes such as unique apartment identifiers, project associations, physical dimensions (e.g., area, room sizes), and specifications like floor number, number of rooms, and apartment type."""}
        }
        result = []
        table_ids=[1,2]
        # print(column_details)
        for table_id in table_ids:
            # print(table_id)
            table_name= table_details[table_id]["table_name"]
            table_desc=table_details[table_id]["table_desc"]

            print("Table Name ::", table_name,"ID ::",table_id)

            top_3=self.__get_top3(table_name)

            # Append the table details and its columns to the result
            result.append({
                "table_id": table_id,
                "table_name":table_name,
                "table_desc": table_desc,
                "top-3":top_3.to_csv(index=False),
                "columns": [
                    {
                        "col_id": column["column_id"],
                        "col_name": column["column_name"],
                        "col_type": column['dtypes'],
                        "col_desc": column["column_desc"]
                    }
                    for column in column_details if column["table_id"]==table_id
                ]
            })
        
        return json.dumps(result)

    def get_prompt(self):
        data_dictionary=self.__get_table_details_with_columns()
        data_dictionary_prompt = ''
        for table in json.loads(data_dictionary):
            data_dictionary_prompt += f"Table Name:{table['table_name']}\nTable Description:{table['table_desc']}"
            data_dictionary_prompt += "\nColumns(with data type and description):\n"
            for column in table['columns']:
                data_dictionary_prompt += f"{column['col_name']} ({column['col_type']}) : {column['col_desc']}\n"
            data_dictionary_prompt += f"""\n/* \n3 rows from {table['table_name']} table:\n"""
            data_dictionary_prompt+=table['top-3']
            data_dictionary_prompt += "*/ \n\n"
        return data_dictionary_prompt