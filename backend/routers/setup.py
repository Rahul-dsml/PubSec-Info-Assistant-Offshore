from fastapi import APIRouter, Depends
from approaches.agent import csv_to_sqlite

router = APIRouter(prefix='/setup', tags=['Setup'])


async def create_service():
    try:
        csv_file_path="translated_file.csv"
        sqlite_db_path="real_estate.db"
        csv_to_sqlite(csv_file_path,sqlite_db_path)
        print("Set up the database")
    except Exception as e:
        print(f"An error occurred in user table Creation: {e}")


        