from groq import Groq
import os
import sqlite3
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import json
import ast

load_dotenv()


client = Groq(
    api_key= os.getenv("GROQ_API_KEY"),
)


model = ChatGroq(
    model="llama-3.2-90b-vision-preview",# "llama-3.3-70b-versatile",
    temperature=0.1,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.getenv("GROQ_API_KEY")
    # other params...
)
def csv_to_sqlite():
    # Load CSV into pandas DataFrame
    df = pd.read_csv(r"C:\Users\rahul\Desktop\Offshore\PubSec-Info-Assistant-Offshore\PubSec-Info-Assistant-Offshore-1\backend\df_english_v2.csv", encoding='utf-8')
    # df = pd.read_csv()
    # Create SQLite database and write the DataFrame to it
    conn = sqlite3.connect(r"C:\Users\rahul\Desktop\Offshore\PubSec-Info-Assistant-Offshore\PubSec-Info-Assistant-Offshore-1\backend\real_estate.db")
    df.to_sql('real_estate', conn, if_exists='replace', index=False)


csv_to_sqlite()

class DataDictionaryPrompt():

    def __init__(self,) -> None:
        # self.file_path=st.secrets.file.file_path or os.getenv('file_path')
        # self.sheet_name=st.secrets.file.sheet_name or os.getenv('sheet_name')
        self.dict_file_path="Data_Dictionary_v2.xlsx"
        
    def __get_data_dict(self):
        try:
            # Load the Excel sheet into a pandas DataFrame
            df = pd.read_excel(r"C:\Users\rahul\Desktop\Offshore\PubSec-Info-Assistant-Offshore\PubSec-Info-Assistant-Offshore-1\backend\Data_Dictionary_v2.xlsx")
            df=df.reset_index()
            df=df.rename({"index":"col_id","Field Name":"column_name","Data Type":"col_dtype","Description":"col_desc"},axis=1)
            # Create an in-memory SQLite database
            # conn = sqlite3.connect(":memory:")
            conn = sqlite3.connect(r"C:\Users\rahul\Desktop\Offshore\PubSec-Info-Assistant-Offshore\PubSec-Info-Assistant-Offshore-1\backend\real_estate.db")

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
            conn = sqlite3.connect(r"C:\Users\rahul\Desktop\Offshore\PubSec-Info-Assistant-Offshore\PubSec-Info-Assistant-Offshore-1\backend\real_estate.db")
            
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
    
def Decision_Agent(user_query, language='English', history=None):
    # if history:
    prompt = f"""You are an honest, persuasive, and dedicated Real-Estate agent AI conversational assistant at NHC Housing Company. Your task is to continue the ongoing conversation with the user regarding the property selection or recommendation or both.
    
    Conversation History: {history}
    User Query: {user_query}
    Based on this conversation history (if any) and current user query, you must follow below guidelines strictly:
    1. Always carefully analyze both the `Conversation History` and the `User Query`. As conversation history may contain the already recommended properties.
    2. Use context from the Conversation History to avoid redundant information and offer smooth, follow-up answers.
    3. Always generate **very short**, crisp, precise, polite, generous and real estate professional response. Do not generate lengthy response.
    
    YOU MUST GENERATE RESPONSE IN JSON FORMAT AS FOLLOWS:
    {{"SQL_QUERY": "BOOLEAN YES OR NO | 'YES' if conversation history and current User Query can be transformed to SQL Query else 'NO'",
      "Response": "Your response to the conversation or initiating the conversation"}}

    THERE GENERATED RESPONSE MUST ALWAYS BE IN JSON AS DESCRIBED ABOVE WITH NO TAGS, EXPLANATION, ETC.
    
    """
    chat_completion = client.chat.completions.create(
        messages=[{'role': 'system', 'content': f'You are a Real Estate agent who talk in {language} language and helps customer in finding and buying properties in a very professional and polite way.'},
                {"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile", # "llama-3.2-90b-vision-preview",
        temperature=0,
        max_tokens=1024,
    )
    return chat_completion.choices[0].message.content.strip()

def query_classifier(user_query):
 
    prompt = f"""You are an intelligent AI system designed to classify user queries about real estate into one of two categories: Search-based or Recommendation-based.
 
    -   Search-based queries are those where the user provides specific, concrete filters, such as price range, location, number of rooms, or property size, to search for a property.
 
        Example:
        "I need a villa in Dammam with an area larger than 350 square meters."
        "Show me apartments priced under 2 million SAR in Riyadh."
        "Find me a villa with 5 bedrooms and 4 bathrooms in Jeddah."
    
    -   Recommendation-based queries are those where the user provides contextual information, such as their salary, family size, or lifestyle preferences, and expects you to recommend a suitable property.
 
        Example:
        "My salary is 10,000 SAR; please suggest a property."
        "I have 3 children and need an affordable apartment near schools in Mecca."
        "Recommend a villa for a family of 5 with a budget under 3 million SAR."
        
    Task:
    Given a user query, classify it into either "Search-based" or "Recommendation-based" based on its intent and structure.
 
    Output format:
 
    If the query is search-based, respond with: Search-based
    If the query is recommendation-based, respond with: Recommendation-based
    Examples:
 
    Question: I need a villa with a garden in Khobar.
    Output: Search-based
 
    Question: My monthly income is 15,000 SAR, and I prefer a villa in Riyadh.
    Output: Recommendation-based
 
    Question: Find me an apartment with at least 3 bedrooms in the Almasief district.
    Output: Search-based
 
    Question: I have 2 kids and a budget of 1.5 million SAR. Suggest an apartment in Jeddah.
    Output: Recommendation-based
 
    When a user provides a question, analyze it carefully and classify it accurately. Provide no extra explanations or text, just the classification output.
    
 
    Question: {user_query}
    Output:
    """
 
    chat_completion = client.chat.completions.create(
        messages=[{'role': 'system', 'content': 'You are a text classifier.'},
                {"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile", # "llama-3.2-90b-vision-preview",
        temperature=0,
        max_tokens=1024,
    )
    return chat_completion.choices[0].message.content.strip()

def refine_question(history = [],user_query = 'Hi, I am looking for properties in Riyadh region'):

    prompt=f"""You are a Real Estate helpful assistant who helps user to recommend best properties based on user property preferences. Your task is to write the final user refined query based on the user conversation history and current user input. 
    
    Instructions:
    1. Always write the final query in english language.
    2. In final query must contain all user defined criteria of property preferences from conversation history given and final user input.
    3. The final output must be the final refined query. Do not add any extra text.
    
    # Below is the user conversational history:
    {str(history)}
    
    user input:{user_query}
    refine query:
    """
    
        
    chat_completion = client.chat.completions.create(
        messages=[{'role': 'system', 'content': "You are a Real Estate helpful assistant"},
                {"role": "user", "content": prompt}],
        model="llama-3.2-90b-vision-preview",
        temperature=0,
        max_tokens=1024,
    )
    return chat_completion.choices[0].message.content.strip()

class CodeGeneratorAgent:
    def __init__(self, llm):
        self.llm = llm

    def generate_sql_query(self, query,dict_prompt, search_based = 'search-based'):
            
        if 'search' in search_based.lower():
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """
                        You are an expert DATA ANALYST for Real Estate. You have access to a database and the capability to interact with the database and write SQL queries.
                        
                        You can find the table and column descriptions/schema below:
                        {db_info}
                        
                        Instructions:
                        1. Use SQL dialect -> {dialect} when writing SQL queries.
                        2. Review the user's query thoroughly to understand its intent. Carefully verify the table names and their descriptions, ensuring accuracy. Focus only on the relevant columns when constructing the SQL query.
                        3. Always use the wildcard operator `LIKE` for filtering, ensuring all values are transformed to lowercase for consistency. For example, apply filters as `WHERE LOWER(city) LIKE '%pune%'` instead of without converting to lowercase.
                        4. Always use `sakani_beneficiary_price` by default unless the user specifies otherwise.
                        5. Always sort the results on price, number of rooms, living area size in DESCENDING ORDER.
                        6. Always filter out the records having any null values.
                        6. Ensure that all filters and conditions derived from the user's query are properly included within the SQL query.
                        7. Ensure the column names in the generated SQL QUERY always matches with the table schema given above.
                        8. Always use `LIMIT 10` in the generated SQL QUERY.
                        8. THE RESPONSE MUST BE STRICTLY ONLY THE SQL QUERY. DO NOT INCLUDE ANY TAGS LIKE ```sql``` OR ANY SORT OF EXPLANATIONS. JUST QUERY, AS IT WILL BE DIRECTLY USED IN SQL QUERY ENGINE.""",
                    ),
                    ("human", "User Query: {query}"),
                ]
            )
        elif 'reco' in search_based.lower():
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """
                        You are an expert DATA ANALYST for Real Estate. You have access to a database and the capability to interact with the database and write SQL queries.
                        
                        You can find the table and column descriptions/schema below:
                        {db_info}
                        
                        Instructions:
                        1. Use SQL dialect -> {dialect} when writing SQL queries.
                        2. Review the user's query thoroughly to understand its intent. Carefully verify the table names and their descriptions, ensuring accuracy. Focus only on the relevant columns when constructing the SQL query.
                        3. Use the following calculation details to interpret user queries and construct SQL queries:
                        - **Purchasing Power**: Calculate financial capacity using the formula:
                            Purchasing Power = 1.8 / (Salary × 0.65 × 240)
                        - **Family Size**: For housing size recommendations, every two individuals require at least one room.
                            Example: A family of 4 requires a minimum of 2 rooms, while a family of 5 requires at least 3 rooms.
                        4. Always dynamically incorporate the derived constraints from calculations (e.g., purchasing power and minimum room requirements) into the SQL query.
                        5. Always use the wildcard operator `LIKE` for filtering, ensuring all values are transformed to lowercase for consistency. For example, apply filters as `WHERE LOWER(city) LIKE '%pune%'` instead of without converting to lowercase.
                        6. Use `sakani_beneficiary_price` by default unless the user specifies otherwise.
                        7. ALWAYS LIMIT THE SQL QUERY TO LIMIT 5.
                        8. Always sort the results in DESCENDING ORDER.
                        9. Ensure that all filters and conditions derived from the user's query are properly included within the SQL query.
                        10. Ensure the column names in the generated SQL QUERY always match with the table schema given above.
                        11. THE RESPONSE MUST BE STRICTLY ONLY THE SQL QUERY. DO NOT INCLUDE ANY TAGS LIKE ```sql``` OR ANY SORT OF EXPLANATIONS. JUST QUERY, AS IT WILL BE DIRECTLY USED IN SQL QUERY ENGINE.
                        """,
                    ),
                    ("human", "User Query: {query}"),
                ]
            )


        # Use the LLM to generate SQL query
        chain = prompt | self.llm
        response = chain.invoke({"db_info": dict_prompt, 
                                 "dialect": "sqllite",
                                 "query": query})
        return response.content.strip()  # Remove extra whitespace or newlines
    
class CodeExecutorAgent:
    def __init__(self):
        self.db_connection = sqlite3.connect(r"C:\Users\rahul\Desktop\Offshore\PubSec-Info-Assistant-Offshore\PubSec-Info-Assistant-Offshore-1\backend\real_estate.db")

    def execute_sql_query(self, sql_query):
        # try:
            # cursor = self.db_connection.cursor()
            # cursor.execute(sql_query)
            # result = cursor.fetchall()  # Fetch all results from the query execution
            result = pd.read_sql_query(sql_query, self.db_connection)
            print("-------------------recommendation data----------------------------")
            print(result)
            if "project_id" in result.columns:
                project_id=tuple(result['project_id'].to_list())
                if str(project_id)[-2]==",":
                    project_id=str(project_id)[:-2]+")"
                print("-------------------Project ids----------------------------")
                print(project_id)
                if len(project_id)>0:
                    project_query=f"select DISTINCT project_id,[Project URL],project_name_eng,project_latitude,project_longitude from real_estate where project_id in {project_id}"
                    cursor = self.db_connection.cursor()
                    cursor.execute(project_query)
                    lat_long_details = cursor.fetchall() 
                    lat_long_details_list=[]
                    for project in lat_long_details:
                        lat_long_details_dict={"project_id":project[0],
                                            "Project URL":project[1],
                                            "project_name_eng":project[2],
                                            "project_latitude":project[3],
                                        "project_longitude":project[4] }
                        lat_long_details_list.append(lat_long_details_dict)
                else:
                    lat_long_details_list=""
            else:
                lat_long_details_list=""

            print("--------------------------lat_long_details_dict------------------------")
            print(lat_long_details_list)
            result1=result.to_csv(index=False)
            summary = result.describe(include = "all")
            return result1, lat_long_details_list, summary.to_csv(index=False)
        
class InsightGeneratorAgent:
    def __init__(self, llm):
        self.llm = llm

    def generate_insight(self, user_query = 'Hi', execution_result= "", chat_language= 'English', chat_history= []):
        if chat_language.lower()=="english":
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """
                        You are an expert real estate sales assistant at NHC Housing company with ENGLISH native language who talks with the user as a real person based on the user query, conversation history and current information from dataset given below:
                        user query: {user_query}
                        conversation history: {chat_history}
                        Current Information: {execution_result}
                        
                        You need to strictly follow below guidelines/ checklist:
                        1. If chat history is none, start with the greeting message "Welcome to NHC, I am your personal AI Assistant! How may I help you today in finding your best properties?"
                        2. Always continue the conversation and do not repeat the information already provided in the chat history unless user specifically asks for it.
                        3. Always try to provide with new details about the units/apartments/villas/townhouses based on the conversation.
                        3. If provided, use the current information to provide the relevant response on apartment level using Current Information.
                        4. Never overload the user with excess information, always provide short and only relevant information like price, number of rooms, completion status, etc. based on the user query and current information.
                        5. Never mention any type of ID or code as it is irrelevant to the user.
                        6. Always provide information about at least 5 records in the 'Current Information' and make sure to include the variety on projects.
                        6. Always convert the price in millions SAR.
                        7. Always assume you are a real person and you are in a conversation. Do not give lengthy responses and too many follow up questions.
                        8. ALWAYS STICK TO THE INFORMATION PROVIDED IN Current Information or conversation history.
                        
                        YOU MUST GENERATE RESPONSE IN JSON FORMAT AS FOLLOWS:
                        {{"SQL_QUERY": "BOOLEAN YES OR NO | 'YES' if conversation history and current User Query can be transformed to SQL Query else 'NO'",
                        "Response": "Your response to the conversation or initiating the conversation"}}

                        THERE GENERATED RESPONSE MUST ALWAYS BE IN JSON AS DESCRIBED ABOVE WITH NO TAGS, EXPLANATION, ETC.
                        """,
                    ),
                ]
            )
        else:
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """
                        You are an expert real estate sales person at NHC Housing company with ARABIC native language who provides convincing recommendations based on the execution_results in response to user's query. The result is from executing an SQL query on an SQLite database, and you need to generate natural language response in ARABIC language from it.
                        ALWAYS CONTINUE THE CONVERSATION, DO NOT REPEAT THE INFORMATION ALREADY PROVIDED UNLESS USER SPECIFICALLY ASKS FOR IT.
                        # Use below instruction to generate the final response:
                        1. Refer to the given data and SQL query, and convert them into a natural language response as if you were explaining the project to a client.
                        2. If there are duplicate project names consolidate the details into a single explanation to provide a clear and concise description of the project.
                        3. If the Execution Result is empty apologize and mention: I'm sorry, I did not find a proper match as per your preferences.
                        4. Do not say 'Based on your query'; instead, use 'Based on your requirements.'
                        5. ALWAYS START WITH TOP 2 BEST MATCH RESULT AND USE OTHER RESULTS AS RECOMMENDATION for eg. ``Great preference(s)! I have found best match results for you {{top 2 best match results}}. I would also like to grab your attention to these projects as well {{other results}}.``
                        6. DO NOT OVERLOAD USER WITH SO MUCH INFORMATION AND CONTINUE THE CONVERSATION ASSUMING YOU ARE IN A REAL PHYSICAL CONVERSATION WITH THE USER.
                        
                        user query: {user_query}
                        sql query: {sql_query}
                        Execution Result: {execution_result}
                        Provide the recommendations as natural language response in ARABIC LANGUAGE based on the execution result.
                        """,
                    ),
                ]
            )

        # Generate insight from execution result
        chain = prompt | self.llm
        response = chain.invoke({"user_query": user_query,
                                 "chat_history": chat_history,
                                 "execution_result": execution_result})
        return response.content.strip()

class Report():
    def __init__(self, id):
        self.db_connection = sqlite3.connect(r"C:\Users\rahul\Desktop\Offshore\PubSec-Info-Assistant-Offshore\PubSec-Info-Assistant-Offshore-1\backend\real_estate.db")
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
        
        ```selected property information: {selected_apartment}
        comparison with similar apartments: {comparison}```
        
        Always, generate the report for the user to provide detailed overview on following aspects:
        1. Bullet points for selected apartment for relevant features like - price, number of rooms, project name, project location(city, district, region), project url, etc.
        2. Price comparison with similar apartments in percentage.
        3. Number of rooms comparison with similar apartments (higher or lower). Do Not provide comparison in percetage or fractions.
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
        




def assistant_chat():
    # Streamlit UI
    st.title("Real Estate Assistant Chat")
    st.markdown("""A chatbot that processes your queries, generates SQL code, executes it, and provides insights.
    Type 'exit' to terminate the chat.
    """)

    # Initialize chat history and default language
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "chat_language" not in st.session_state:
        st.session_state.chat_language = "english"

    # User input
    user_query = st.text_input("You:", key="user_input")

    if user_query:
        if user_query.lower() == "exit":
            st.write("Conversation terminated.")
            st.stop()

        # Generate response
        agent = InsightGeneratorAgent(llm=model)
        response = agent.generate_insight(user_query=user_query, chat_history=st.session_state.chat_history)
        # response = Decision_Agent(user_query, st.session_state.chat_history)

        # Parse response into dictionary
        response = ast.literal_eval(response)
        st.write(f"Bot: {response['Response']}")

        if response['SQL_QUERY'].lower() == "yes":
            st.write("Processing terminate flow logic...")

            query_type = query_classifier(user_query=user_query)
            st.write(query_type)
            refined_user_query = refine_question(user_query=user_query, history=st.session_state.chat_history)

            st.write(f"Refined Query: {refined_user_query}")
            dict_object = DataDictionaryPrompt()
            dict_prompt = dict_object.get_prompt()
            code_generator = CodeGeneratorAgent(llm=model)
            code_executor = CodeExecutorAgent()
            # insight_generator = InsightGeneratorAgent(llm=model)

            sql_query = code_generator.generate_sql_query(
                query=refined_user_query,
                dict_prompt=dict_prompt,
                search_based=query_type
            )

            st.write("Generated SQL Query:")
            st.code(sql_query, language="sql")

            result = code_executor.execute_sql_query(sql_query=sql_query)

            st.write("--- Execution Results ---")
            st.write(result[0])

            insights = agent.generate_insight(
                user_query=user_query, 
                execution_result=result[0], chat_history=st.session_state.chat_history
            )
            insights = ast.literal_eval(insights)
            response['Response'] = insights['Response']
            st.write("Insights:")
            st.write(insights['Response'])

            # # Update the response with insights
          

        # Update chat history
        st.session_state.chat_history.append(
            {"user": user_query, "bot": response['Response']}
        )

    # Display chat history
    st.markdown("### Chat History")
    for entry in st.session_state.chat_history:
        st.markdown(f"**You:** {entry['user']}")
        st.markdown(f"**Bot:** {entry['bot']}")

# Run Streamlit app
if __name__ == "__main__":
    assistant_chat()
