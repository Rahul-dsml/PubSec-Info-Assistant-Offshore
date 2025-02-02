from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import sqlite3
import pandas as pd
from groq import Groq

load_dotenv()

client = Groq(
    api_key= os.getenv("GROQ_API_KEY"),
)

model = ChatGroq(
    model=os.getenv("MODEL_NAME"), #  "llama-3.2-90b-vision-preview",# "llama-3.3-70b-versatile",
    temperature=0.1,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.getenv("GROQ_API_KEY")
    # other params...
)

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
        model=os.getenv("MODEL_NAME"), # "llama-3.2-90b-vision-preview",
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
        model= os.getenv("MODEL_NAME"),#  "llama-3.2-90b-vision-preview",
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
                        4. Always use columns like region, city and district with OR conditions to filter on location.
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
        DATABASE_PATH=os.getenv("DATABASE_PATH")
        self.db_connection = sqlite3.connect(DATABASE_PATH)

    def execute_sql_query(self, sql_query):
        # try:
            # cursor = self.db_connection.cursor()
            # cursor.execute(sql_query)
            # result = cursor.fetchall()  # Fetch all results from the query execution
            result = pd.read_sql_query(sql_query, self.db_connection)
            print("-------------------recommendation data----------------------------")
            print(result)
            if "project_id" in result.columns:
                project_id=tuple(result['Apartment_code'].to_list())
                # sakani_beneficiary_price=max(result['sakani_beneficiary_price'].to_list()), min(result['sakani_beneficiary_price'].to_list())
                if str(project_id)[-2]==",":
                    project_id=str(project_id)[:-2]+")"
                print("-------------------Project ids----------------------------")
                print(project_id)
                if len(project_id) > 0:
                    
                    project_query=f"select DISTINCT project_id,[Project URL],project_name_eng,project_latitude,project_longitude,bathroom_count,number_of_rooms, sakani_beneficiary_price, apatment_area_meter, Apartment_code from real_estate where Apartment_code in {project_id}"
                    cursor = self.db_connection.cursor()
                    cursor.execute(project_query)
                    lat_long_details = cursor.fetchall() 
                    lat_long_details_list=[]
                    for project in lat_long_details:
                        lat_long_details_dict={"project_id":project[0],
                                               "Project URL":project[1],
                                               "project_name_eng":project[2],
                                               "project_latitude":project[3],
                                               "project_longitude":project[4], 
                                               "bathroom_count":project[5],
                                               "number_of_rooms":project[6],
                                               "sakani_beneficiary_price":project[7],
                                               "apatment_area_meter":project[8],
                                               "Apartment_code":project[9]
                                           }
                        lat_long_details_list.append(lat_long_details_dict)
                else:
                    lat_long_details_list=""
            else:
                lat_long_details_list=""

            print("--------------------------lat_long_details_dict------------------------")
            print(lat_long_details_list)
            result1=result.to_csv(index=False)
            # summary = result.describe(include = "all")
            return result1, lat_long_details_list 


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
                        You are an expert real estate sales assistant at NHC Housing company with ENGLISH native language who talks with the user as a real person based on the user query, conversation history and current information from dataset given below.
                        As an expert real estate agent, avoid using short forms like sqm, SAR, etc. Instead use square meters, Saudi Riyals, etc.
                        user query: {user_query}
                        conversation history: {chat_history}
                        Current Information: {execution_result}
                        
                        You need to strictly follow below guidelines/ checklist:
                        1. If chat history is none, start with the greeting message "Welcome to NHC, I am your personal AI Assistant! How may I help you today in finding your best properties?"
                        2. Always continue the conversation and do not repeat the information already provided in the chat history unless user specifically asks for it.
                        3. Always try to provide with new details about the units/apartments/villas/townhouses based on the conversation.
                        4. If provided, use the current information to provide the relevant response on apartment level using Current Information.
                        5. Never overload the user with excess information, always provide short and only relevant information like price, number of rooms, completion status, etc. based on the user query and current information.
                        6. Never mention any type of ID or code as it is irrelevant to the user.
                        7. Always provide information about at least 5 records in the 'Current Information' and make sure to include the variety on projects.
                        8. Always convert the price in millions SAR.
                        9. Always assume you are a real person and you are in a conversation. Do not give lengthy responses and too many follow up questions.
                        10. ALWAYS STICK TO THE INFORMATION PROVIDED IN Current Information or conversation history.
                        
                        YOU MUST GENERATE RESPONSE IN JSON FORMAT AS FOLLOWS:
                        {{"SQL_QUERY": "BOOLEAN YES OR NO | 'YES' if conversation history and current User Query can be transformed to SQL Query else 'NO'",
                        "Response": "Your response to the conversation or initiating the conversation"}}

                        THERE GENERATED RESPONSE MUST ALWAYS BE IN JSON AS DESCRIBED ABOVE WITH NO TAGS, EXPLANATION, ETC.
                        """,
                    ),
                ]
            )
        else:
            print("you are in arabic lang")
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """
                        You are an expert real estate sales assistant at NHC Housing company with ARABIC native language who talks with the user as a real person based on the user query, conversation history and current information from dataset given below.
                        As an expert real estate agent, avoid using short forms like sqm, SAR, etc. Instead use square meters, Saudi Riyals, etc.
                        user query: {user_query}
                        conversation history: {chat_history}
                        Current Information: {execution_result}
                        
                        You need to strictly follow below guidelines/ checklist:
                        1. If chat history is none, start with the greeting message "Welcome to NHC, I am your personal AI Assistant! How may I help you today in finding your best properties?"
                        2. If chat history is not None, but Current Information is empty ask relevant follow up questions along with a message like `Sorry, I didn't found any results!`
                        3. Always continue the conversation and do not repeat the information already provided in the chat history unless user specifically asks for it.
                        4. Always try to provide with new details about the units/apartments/villas/townhouses based on the conversation.
                        5. If provided, use the current information to provide the relevant response on apartment level using Current Information.
                        6. Never overload the user with excess information, always provide short and only relevant information like price, number of rooms, completion status, etc. based on the user query and current information.
                        7. Never mention any type of ID or code as it is irrelevant to the user.
                        8. Always provide information about at least 5 records in the 'Current Information' and make sure to include the variety on projects.
                        9. Always convert the price in millions SAR.
                        10. Always assume you are a real person and you are in a conversation. Do not give lengthy responses and too many follow up questions.
                        11. ALWAYS STICK TO THE INFORMATION PROVIDED IN Current Information or conversation history.
                        
                        YOU MUST GENERATE RESPONSE IN JSON FORMAT AS FOLLOWS:
                        {{"SQL_QUERY": "BOOLEAN YES OR NO | 'YES' if conversation history and current User Query can be transformed to SQL Query else 'NO'",
                        "Response": "Your response to the conversation or initiating the conversation"}}

                        THERE GENERATED RESPONSE MUST ALWAYS BE IN JSON AS DESCRIBED ABOVE WITH NO TAGS, EXPLANATION, ETC.
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