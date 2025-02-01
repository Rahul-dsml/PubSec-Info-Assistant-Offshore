import os
import sqlite3
import pandas as pd
from groq import Groq
from pydantic import BaseModel, Field
from typing import Any



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

        
        Always, generate the report in MARKDOWN format for the user to provide detailed overview on following aspects:
        1. Bullet points for selected apartment for relevant features like - price, number of rooms, project name, project location(city, district, region), project url, etc.
        2. Price comparison with similar apartments in percentage.
        3. Number of rooms comparison with similar apartments (higher or lower). Do Not provide comparison in percentage or fractions.
        4. Living area comparison with similar apartments in percentage.
        5. Conclusion for summary of comparison and convincing the user as a Real Estate Agent.
        Also, provide the conclusion based on these results.
        The Report must not exceed the word limit 500 and MUST BE IN MARKDOWN FORMAT.
        """
        
            
        chat_completion = client.chat.completions.create(
            messages=[{'role': 'system', 'content': "You are a Real Estate helpful assistant"},
                    {"role": "user", "content": prompt}],
            model=os.getenv("MODEL_NAME"),
            temperature=0,
            max_tokens=1024,
        )
        return chat_completion.choices[0].message.content.strip()

        