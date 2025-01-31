import os
import sqlite3
import pandas as pd
from groq import Groq
from pydantic import BaseModel, Field
from typing import Any


# class ApartmentDetails(BaseModel):
#     apartment_code: str = Field(..., description="Unique identifier for the apartment")
#     region_id_eng: str = Field(..., description="Region ID in English")
#     living_area: float = Field(..., description="Living area in square meters")
#     number_of_rooms: int = Field(..., description="Number of rooms in the apartment")
#     sakani_beneficiary_price: float = Field(..., description="Price for Sakani beneficiaries")
#     non_sakani_beneficiary_price: float = Field(..., description="Price for non-Sakani beneficiaries")


# class Report:
#     """
#     A class to generate a real estate report comparing a selected apartment with similar apartments in the region.
#     """
    
#     def __init__(self, apartment_id: str):
#         """
#         Initializes the Report class with a database connection and apartment ID.

#         :param apartment_id: Unique identifier for the apartment.
#         """
#         database_path = os.getenv("DATABASE_PATH")
#         if not database_path:
#             raise ValueError("Database path is not set in environment variables.")
        
#         self.db_connection = sqlite3.connect(database_path)
#         self.apartment_id = apartment_id
#         self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

#     def get_unit_details(self) -> list[ApartmentDetails]:
#         """
#         Fetches details of the selected apartment from the database.

#         :return: List containing the apartment details as a Pydantic model.
#         """
#         sql_query = f"""
#             SELECT * FROM real_estate 
#             WHERE apartment_code = ?
#         """
#         df = pd.read_sql_query(sql_query, self.db_connection, params=(self.apartment_id,))
        
#         if df.empty:
#             raise ValueError("No data found for the given apartment ID.")
        
#         return [ApartmentDetails(**row) for row in df.to_dict(orient="records")]

#     def avg_price_similar_apartments(self) -> dict[str, Any]:
#         """
#         Calculates the average price, number of rooms, and living area for similar apartments.

#         :return: Dictionary containing the average values.
#         """
#         unit_data = self.get_unit_details()[0]
        
#         sql_query = f"""
#             SELECT 
#                 AVG(sakani_beneficiary_price) AS avg_sakani_beneficiary_price,
#                 AVG(non_sakani_beneficiary_price) AS avg_non_sakani_beneficiary_price,
#                 AVG(living_area) AS avg_living_area,
#                 AVG(number_of_rooms) AS avg_number_of_rooms
#             FROM real_estate
#             WHERE region_id_eng = ?
#               AND living_area BETWEEN ? AND ?
#         """
#         df = pd.read_sql_query(
#             sql_query, self.db_connection, 
#             params=(unit_data.region_id_eng, unit_data.living_area - 10, unit_data.living_area + 10)
#         )
        
#         return df.to_dict(orient="records")[0] if not df.empty else {}

#     def generate_report(self) -> str:
#         """
#         Generates a real estate comparison report using an AI assistant.

#         :return: Generated report text.
#         """
#         selected_apartment = self.get_unit_details()[0].dict()
#         comparison = self.avg_price_similar_apartments()

#         prompt = f"""
#         You are a Real Estate assistant helping users analyze properties. 
#         Below is the information about a selected apartment and a comparison with similar apartments:

#         Selected Property Information:
#         {selected_apartment}
        
#         Comparison with Similar Apartments:
#         {comparison}
        
#         Generate a concise report (under 100 words) covering:
#         1. Bullet points listing key apartment features (price, rooms, project name, location, etc.).
#         2. Price comparison with similar apartments (percentage difference).
#         3. Room count comparison (indicate if higher or lower, without percentages).
#         4. Living area comparison (percentage difference).
#         5. A concluding statement summarizing insights.
#         """

#         response = self.client.chat.completions.create(
#             messages=[
#                 {'role': 'system', 'content': "You are a Real Estate helpful assistant"},
#                 {"role": "user", "content": prompt}
#             ],
#             model="llama-3.2-90b-vision-preview",
#             temperature=0,
#             max_tokens=1024,
#         )
        
#         return response.choices[0].message.content.strip()

#     def __del__(self):
#         """
#         Closes the database connection when the object is deleted.
#         """
#         self.db_connection.close()



import sqlite3
import pandas as pd
import os
from groq import Groq

client = Groq(
    api_key= os.getenv("GROQ_API_KEY"),
)


class Report():
    def __init__(self, id):
        self.db_connection = sqlite3.connect(os.getenv("database_path"))
        self.id = id

    def get_unit_details(self):
        sql_query=f"Select * from real_estate where apartment_code='{self.id}'"
        df=pd.read_sql_query(sql_query,self.db_connection)
        unit_data=df.to_json(orient="records")
        # print(unit_data)
        return unit_data
    
    def avg_price_similar_apartments(self):
        unit_data=self.get_unit_details()
        unit_data=eval(unit_data)
        region_id_eng=unit_data[0]['region_id_eng']
        living_area=unit_data[0]['living_area']
        Apartment_code=unit_data[0]['Apartment_code']
        # print(region_id_eng)
        sql_query=f"""
    SELECT AVG(sakani_beneficiary_price) AS avg_sakani_beneficiary_price ,
            AVG(non_sakani_beneficiary_price) AS avg_non_sakani_beneficiary_price,
            AVG(living_area) AS avg_living_area,
            AVG(number_of_rooms) AS avg_number_of_rooms
    FROM real_estate  WHERE region_id_eng = '{region_id_eng}' 
      AND living_area BETWEEN {living_area - 10} AND {living_area + 10}

"""
        # sql_query=f"select apartment_code,project_name_eng,region_id_eng, sakani_beneficiary_price ,non_sakani_beneficiary_price  from real_estate"
        df=pd.read_sql_query(sql_query,self.db_connection)
        
        unit_price_data=df.to_json(orient="records")
        return unit_price_data
    
    def generate_report(self):
        
        selected_apartment = self.get_unit_details()
        comparison = self.avg_price_similar_apartments()

        prompt=f"""You are a Real Estate helpful assistant who helps user in analysing the results and generate a report.
        You will be provided with the information of user selected property and information about the average price, average number of rooms and average living area of similar apartments.
        
        
selected property information: {selected_apartment}
        comparison with similar apartments: {comparison}

        
        Always, generate the report for the user to provide detailed overview on following aspects:
        1. Bullet points for selected apartment for relevant features like - price, number of rooms, project name, project location(city, district, region), project url, etc.
        2. Price comparison with similar apartments in percentage.
        3. Number of rooms comparison with similar apartments (higher or lower). Do Not provide comparison in percentage or fractions.
        4. Living area comparison with similar apartments in percentage.
        Also, provide the conclusion based on these results.
        The Report must not exceed the word limit 100.
        """
        
            
        chat_completion = client.chat.completions.create(
            messages=[{'role': 'system', 'content': "You are a Real Estate helpful assistant"},
                    {"role": "user", "content": prompt}],
            model="llama-3.2-90b-vision-preview",
            temperature=0,
            max_tokens=1024,
        )
        return chat_completion.choices[0].message.content.strip()

        