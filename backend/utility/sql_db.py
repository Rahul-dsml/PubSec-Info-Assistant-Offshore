import sqlite3
import pandas as pd
import os
import json
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
load_dotenv()

class CSVToSQLiteConfig(BaseModel):
    csv_file_path: str
    database_path: str


def csv_to_sqlite():
    """
    Reads a CSV file and writes its contents to an SQLite database.
    
    Raises:
        ValueError: If the database path is not set in environment variables.
        FileNotFoundError: If the CSV file is not found.
    """
    csv_file_path = os.getenv("CSV_FILE_PATH")
    database_path = os.getenv("DATABASE_PATH")
    
    if not database_path:
        raise ValueError("Database path is not set in environment variables.")
    
    if not csv_file_path or not os.path.exists(csv_file_path):
        raise FileNotFoundError("CSV file path is not valid or does not exist.")
    
    # Load CSV into pandas DataFrame
    df = pd.read_csv(csv_file_path, encoding='utf-8')
    
    # Create SQLite database and write the DataFrame to it
    with sqlite3.connect(database_path) as conn:
        df.to_sql('real_estate', conn, if_exists='replace', index=False)




