import os
import sqlite3
import pandas as pd
from groq import Groq
from pydantic import BaseModel, Field
from typing import Any
import ast



import sqlite3
import pandas as pd
import os
from groq import Groq

client = Groq(
    api_key= os.getenv("GROQ_API_KEY"),
)


class Report():
    def __init__(self, id):
        path = os.getenv("DATABASE_PATH")
        self.db_connection = sqlite3.connect(path)
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
    
    def similar_apartments(self):
        unit_data = self.get_unit_details()
        unit_data = eval(unit_data)
        region_id_eng = unit_data[0]['region_id_eng']
        living_area = unit_data[0]['living_area']
        price = unit_data[0]['sakani_beneficiary_price']
        rooms = unit_data[0]['number_of_rooms']
        Apartment_code = unit_data[0]['Apartment_code']
        # print(region_id_eng)
        sql_query = f"""
    SELECT *
    FROM real_estate  WHERE region_id_eng = '{region_id_eng}' 
      AND living_area BETWEEN {living_area - 10} AND {living_area + 10}
      AND sakani_beneficiary_price BETWEEN {price - 0.1*price} AND {price + 0.1*price}
      AND number_of_rooms BETWEEN {rooms - 2} AND {rooms + 2}
      AND Apartment_code <> {Apartment_code}
    SORT BY living_area DESC, number_of_rooms DESC, sakani_beneficiary_price ASC

"""
        # sql_query=f"select apartment_code,project_name_eng,region_id_eng, sakani_beneficiary_price ,non_sakani_beneficiary_price  from real_estate"
        df=pd.read_sql_query(sql_query,self.db_connection)
        
        similar_prop = df.to_json(orient="records")
        return similar_prop
    
    def generate_report(self):
        
        selected_apartment = self.get_unit_details()
        comparison = self.avg_price_similar_apartments()
        similar_properties= self.similar_apartments()

        prompt=f"""You are a Real Estate helpful assistant who helps user in analysing the results and generate a report.
        You will be provided with the information of user selected property, information about the average price, average number of rooms and average living area of similar apartments and information about similar properties.
        
        user selected property information: {selected_apartment}
        comparison with similar property: {comparison}
        similar properties: {similar_properties}
    
        Always, generate the report in MARKDOWN format for the user to provide detailed overview on following aspects:
        1. Bullet points for selected apartment for relevant features like - price, number of rooms, project name, project location(city, district, region), project url, etc.
        2. Price comparison with similar apartments in percentage.
        3. Number of rooms comparison with similar apartments (higher or lower). Do Not provide comparison in percentage or fractions.
        4. Living area comparison with similar apartments in percentage.
        5. Conclusion for summary of comparison and convincing the user as a Real Estate Agent.
        6. Always recommend best 3 suitable properties considering the properties selected by the user including the project name, apartment_code, project url, price, number of rooms, project location(city, district, region) etc.
        7. NEVER RECOMMEND THE ALREADY SELECTED APARTMENT IN THE RECOMMENDATIONS.
        Also, provide the conclusion based on these results.
        The Report must not exceed the word limit 500 and MUST BE IN MARKDOWN FORMAT.
        
        The output must be in JSON FORMAT as below:
        {{"Current_apartment_details": "Information regarding current apartment",
          "Comparison": "Price, Number of Rooms, and Area comparison with similar apartments",
          "Summary": "Summary of the comparisons",
          "Recommendations": "Agent recommending Top 3 suitable Recommendations strictly from the similar properties convincing the user to consider."}}
          
        THE OUTPUT MUST BE STRICTLY JSON AS DESCRIBED ABOVE, WITHOUT ANY ADDITIONAL TEXT OR TAGS.
        """
        
            
        chat_completion = client.chat.completions.create(
            messages=[{'role': 'system', 'content': "You are a Real Estate helpful assistant"},
                    {"role": "user", "content": prompt}],
            model=os.getenv("MODEL_NAME"),
            temperature=0,
            max_tokens=1024,
        )
        
        response = chat_completion.choices[0].message.content.strip()
        response = response[response.find("{"):response.find("}")+1]
        response = ast.literal_eval(response)
        return response

        