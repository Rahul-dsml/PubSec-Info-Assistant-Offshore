from fastapi import APIRouter, Depends
from utility.sql_db import csv_to_sqlite

router = APIRouter(prefix='/setup', tags=['Setup'])


async def create_service():
    try:
        csv_to_sqlite()
        print("Set up the database")
    except Exception as e:
        print(f"An error occurred in user table Creation: {e}")
