from groq import Groq
import os
import sqlite3
import pandas as pd
from utility.chat_helper import DataDictionaryPrompt
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
    model="llama-3.3-70b-versatile",
    temperature=0.1,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key="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"
    # other params...
)


class CodeGeneratorAgent:
    def __init__(self, llm):
        self.llm = llm

    def generate_sql_query(self, query,dict_prompt):
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
                    3. Always use `sakani_beneficiary_price` by default unless the user specifies otherwise.
                    4. THE GENERATED SQL QUERY MUST ALIGN WITH THE USER'S QUERY BASED ON THE SCHEMA PROVIDED ABOVE.
                    5. ALWAYS LIMIT THE SQL QUERY TO LIMIT 5.
                    6. THE RESPONSE MUST BE STRICTLY ONLY THE SQL QUERY. DO NOT INCLUDE ANY TAGS LIKE ```sql``` OR ANY SORT OF EXPLANATIONS. JUST QUERY, AS IT WILL BE DIRECTLY USED IN SQL QUERY ENGINE.
                    7. Always use the wildcard operator `LIKE` for filtering, ensuring all values are transformed to lowercase for consistency. For example, apply filters as `WHERE LOWER(city) LIKE '%pune%'` instead of without converting to lowercase.
                    8. Do not mention SELECT * everytime. Based on user intent retrieve the all required important information from the data.
                    9. Always apply the `DISTINCT` clause to `project_id` column to ensure duplicate values are excluded.
                    10. Ensure that all filters and conditions derived from the user's query are properly included within the SQL query.
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

# Code Executor Agent (SQL Query Executor)
class CodeExecutorAgent:
    def __init__(self):
        self.db_connection = sqlite3.connect(r"D:\30. Open Source llm -RAG\PubSec-Info-Assistant-Offshore\backend\real_estate.db")

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
            result=result.to_csv(index=False)
            return result, lat_long_details_list
        # except Exception as e:
        #     return f"Error executing SQL query: {str(e)}"



# Insight Generator Agent
class InsightGeneratorAgent:
    def __init__(self, llm):
        self.llm = llm

    def generate_insight(self, user_query, sql_query, execution_result, chat_language = 'english'):
        if chat_language.lower()=="english":
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """
                        You are a real estate sales person with ENGLISH native language for converting the result into a natural language response to user's query. The result is from executing an SQL query on an SQLite database, and you need to generate natural language response in english language from it.

                        # Use below instruction to generate the final response:
                        1. Refer to the given data and SQL query, and convert them into a natural language response as if you were explaining the project to a client.
                        2. If there are duplicate project names consolidate the details into a single explanation to provide a clear and concise description of the project.
                        3. If the Execution Result is empty apologize and mention: I'm sorry, I did not find a proper match as per your preferences.
                        4. Do not say 'Based on your query'; instead, use 'Based on your requirements.'
                        
                        user query: {user_query}
                        sql query: {sql_query}
                        Execution Result: {execution_result}
                        Provide the recommendations as natural language response in english LANGUAGE based on the execution result.
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
                        You are a real estate assistant with ARABIC native language for converting the result into a natural language response to user's query.

                        # Use below instruction to generate the final response:
                        1. Refer to the given data and SQL query, and convert them into a natural language response as if you were explaining the project to a client.
                        2. If there are duplicate project names consolidate the details into a single explanation to provide a clear and concise description of the project.
                        3. If the Execution Result is empty apologize and mention: I'm sorry, I did not find a proper match as per your preferences.
                        4. Do not say 'Based on your query'; instead, use 'Based on your requirements.'
                        5.  The result is from executing an SQL query on an SQLite database and you need to generate natural language response in arabic language from it.


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
                                 "sql_query": sql_query,
                                 "execution_result": execution_result})
        return response.content.strip()

# Convert CSV to SQLite Database
def csv_to_sqlite(csv_file_path, sqlite_db_path):
    # Load CSV into pandas DataFrame
    df = pd.read_csv(csv_file_path, encoding='utf-8')
    # df = pd.read_csv()
    # Create SQLite database and write the DataFrame to it
    conn = sqlite3.connect(sqlite_db_path)
    df.to_sql('real_estate', conn, if_exists='replace', index=False)



def refine_question(history,user_query):
    
#     history.append({'role': 'user', 'content': user_query})
    
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



# Main Logic
# def main(user_query, csv_file_path, sqlite_db_path,chat_language):
#     # Step 1: Convert CSV to SQLite
#     db_connection, sample_records = csv_to_sqlite(csv_file_path, sqlite_db_path)
#     print(sample_records)
#     # Step 2: Get database schema (tables and column info)
#     db_info = get_db_schema(db_connection)
#     print("database info: \n", db_info)
#     # Initialize agents
#     code_generator = CodeGeneratorAgent(llm=model)
#     code_executor = CodeExecutorAgent(db_connection=db_connection)
#     insight_generator = InsightGeneratorAgent(llm=model)

#     # Step 3: Generate SQL Query (Agent A)
#     generated_sql_query = code_generator.generate_sql_query(query=user_query, db_info=db_info, sample_records=sample_records)
#     print("Generated SQL Query:\n", generated_sql_query)
#     if "terminate-flow" not in str(generated_sql_query).lower():
#         # Step 4: Execute the SQL query (Agent B)
#         execution_result = code_executor.execute_sql_query(generated_sql_query)
#         # print("Execution Result:\n", execution_result)

#         # Step 5: Generate insights from the execution result (Agent C)
#         insight = insight_generator.generate_insight(user_query=user_query, sql_query=generated_sql_query, execution_result=execution_result,chat_language=chat_language)
#         # print("Insight:\n", insight)

#         return insight
#     else:
#         return generated_sql_query

filter_data=[]

def assistant_chat():
    chat_history = []
    chat_language = "english"  # Default language for simplicity

    while True:
        # Simulate user input
        user_query = input("You: ")
        if user_query.lower() == "exit":
            print("Conversation terminated.")
            break
        
        if len(filter_data)==0:
            # Generate response
            response = Decision_Agent(user_query, chat_history)

            response = ast.literal_eval(response)
            print(response)
            print(f"Bot: {response['Response']}")

        if response['SQL_QUERY'].lower()== "yes":
            print("Processing terminate flow logic...")
            # response = response['Response'].lower().replace("terminate flow", "").strip().capitalize()
            refined_user_query = refine_question(chat_history, user_query)
            print(f"Refined Query: {refined_user_query}")
            code_generator = CodeGeneratorAgent(llm=model)
            code_executor = CodeExecutorAgent()
            insight_generator = InsightGeneratorAgent(llm=model)
            # Step 3: Generate SQL Query (Agent A)
            generated_sql_query = code_generator.generate_sql_query(query=refined_user_query, dict_prompt=dict_prompt)
            print("Generated SQL Query:\n", generated_sql_query)

            # Step 4: Execute the SQL query (Agent B)
            execution_result = code_executor.execute_sql_query(generated_sql_query)
            filter_data.append(execution_result)
            print("--------------------------------------")
            print(execution_result)
            
            # Step 5: Generate insights from the execution result (Agent C)
            insight = insight_generator.generate_insight(user_query=user_query, sql_query=generated_sql_query, execution_result=execution_result,chat_language=chat_language)
            print("Generated insight:",insight)
            response['Response']=insight

        # Update chat history
        chat_history.append({"user": user_query, "bot": response['Response']})
        

def Decision_Agent(user_query, language='English', history=None):
    # if history:
    prompt = f"""You are an honest, persuasive, and dedicated Real-Estate agent AI assistant. Your task is to continue the ongoing conversation with the user regarding the property selection or recommendation or both.
    
    Conversation History: {history}
    User Query: {user_query}
    Based on this conversation history (if any) and current user query, you must follow below guidelines strictly:
    1. Always carefully analyze both the `Conversation History` and the `User Query`. As conversation history may contain the already recommended properties.
    2. Always review the Conversation History to determine if the user's property preferences (location, budget, property type, etc.) have already been collected. If Yes, avoid asking the user any follow up question for their preferences again.
    3. If any of these details for user's property preferences are missing, response in a friendly dialogue to collect the missed information.
    4. Use context from the Conversation History to avoid redundant information and offer smooth, follow-up answers.
    5. Always generate **very short**, crisp, precise, polite, generous and real estate professional response. Do not generate lengthy response.
    
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
