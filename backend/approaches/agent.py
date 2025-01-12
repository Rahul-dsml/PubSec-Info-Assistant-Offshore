from groq import Groq
import os
import sqlite3
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from dotenv import load_dotenv

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

    def generate_sql_query(self, query, db_info, sample_records):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are an assistant for generating SQL queries for an SQLite database.
                    The database schema and details are provided below:
                    Table name: dataTable
                    Schema: {db_info}
                    Sample records: {sample_records}
                    1. THE GENERATED SQL QUERY MUST ALIGN WITH THE USER'S QUERY BASED ON THE SCHEMA PROVIDED ABOVE.
                    2. ALWAYS LIMIT THE SQL QUERY TO LIMIT 5.
                    3. THE RESPONSE MUST BE STRICTLY ONLY THE SQL QUERY. DO NOT INCLUDE ANY TAGS LIKE ```sql``` OR ANY SORT OF EXPLANATIONS. JUST QUERY, AS IT WILL BE DIRECTLY USED IN SQL QUERY ENGINE.
                    """,
                ),
                ("human", "User Query: {query}"),
            ]
        )

        # Use the LLM to generate SQL query
        chain = prompt | self.llm
        response = chain.invoke({"db_info": db_info, 
                                 "sample_records": sample_records,
                                 "query": query})
        return response.content.strip()  # Remove extra whitespace or newlines

# Code Executor Agent (SQL Query Executor)
class CodeExecutorAgent:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def execute_sql_query(self, sql_query):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(sql_query)
            result = cursor.fetchall()  # Fetch all results from the query execution
            return result
        except Exception as e:
            return f"Error executing SQL query: {str(e)}"

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
                        You are a real estate assistant with ENGLISH native language for converting the result into a natural language response to user's query. The result is from executing an SQL query on an SQLite database, and you need to generate natural language response in english language from it.

                        # Use below instruction to generate the final response:
                        1. Use bullet point to show the recommendations.
                        2. Include only user specific property preferences like location, price range, type of property in final recommendations until user not ask specifically.

                        user query: {user_query}
                        sql query: {sql_query}
                        Execution Result: {execution_result}
                        Provide the recommendations as natural language response in english LANGUAGE based on the execution result.
                        
                        for e.g.
                        user query: Give me the count of records in dataTable?
                        sql query: SELECT COUNT(*) FROM dataTable
                        Execution Result: [(200,)]
                        Response: The table contains 200 data points.
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
                        The result is from executing an SQL query on an SQLite database, and you need to generate natural language response in arabic language from it.
                        user query: {user_query}
                        sql query: {sql_query}
                        Execution Result: {execution_result}
                        Provide the recommendations as natural language response in ARABIC LANGUAGE based on the execution result.
                        
                        for e.g.
                        user query: "Give me the count of records in dataTable?"
                        sql query: SELECT COUNT(*) FROM dataTable
                        Execution Result: [(200,)]
                        Response: "يحتوي الجدول على 200 نقطة بيانات."
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
    df.to_sql('dataTable', conn, if_exists='replace', index=False)
    sample_records = df.head(5).to_dict(orient="records")
    return conn, sample_records

# Main Logic
def main(user_query, csv_file_path, sqlite_db_path,chat_language):
    # Step 1: Convert CSV to SQLite
    db_connection, sample_records = csv_to_sqlite(csv_file_path, sqlite_db_path)
    print(sample_records)
    # Step 2: Get database schema (tables and column info)
    db_info = get_db_schema(db_connection)
    print("database info: \n", db_info)
    # Initialize agents
    code_generator = CodeGeneratorAgent(llm=model)
    code_executor = CodeExecutorAgent(db_connection=db_connection)
    insight_generator = InsightGeneratorAgent(llm=model)

    # Step 3: Generate SQL Query (Agent A)
    generated_sql_query = code_generator.generate_sql_query(query=user_query, db_info=db_info, sample_records=sample_records)
    print("Generated SQL Query:\n", generated_sql_query)
    if "terminate-flow" not in str(generated_sql_query).lower():
        # Step 4: Execute the SQL query (Agent B)
        execution_result = code_executor.execute_sql_query(generated_sql_query)
        # print("Execution Result:\n", execution_result)

        # Step 5: Generate insights from the execution result (Agent C)
        insight = insight_generator.generate_insight(user_query=user_query, sql_query=generated_sql_query, execution_result=execution_result,chat_language=chat_language)
        # print("Insight:\n", insight)

        return insight
    else:
        return generated_sql_query

# Get database schema
def get_db_schema(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("PRAGMA table_info(dataTable);")
    schema_info = cursor.fetchall()
    db_info = "\n".join([f"Column: {col[1]}, Type: {col[2]}" for col in schema_info])
    
    return db_info


def bot_response(prompt, language='English'):
    
    chat_completion = client.chat.completions.create(
        messages=[{'role': 'system', 'content': f'You are a Real Estate agent who talk in {language} language and helps customer in finding and buying properties in a very professional and polite way.'},
                {"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile", # "llama-3.2-90b-vision-preview",
        temperature=0,
        max_tokens=1024,
    )
    return chat_completion.choices[0].message.content.strip()

def prompt_creation(user_query, history):
    prompt = f"""You are an honest, persuasive, and dedicated Real-Estate agent AI assistant. Your first task is to identify the user defined criteria or preferences like location, budget, property type, etc. But you should not bore the user by so many follow up questions. 

    # Please follow below guidelines strictly:
    1. Always carefully analyze both the `conversation history` and the `current user query`.
    2. Use context from the conversation history to avoid redundant information and offer smooth, follow-up answers.
    3. Before recommending any properties, ensure that essential user details are gathered by checking the following checklist in the conversation history:
        - Always begin the conversation by asking the user for their name to address them in future responses. If the user is not comfortable sharing their name, proceed without insisting and move on to assist them with their query.
        - Always ask the user to provide their specific property preferences in a single question. Include the following details: location, price range, type of property (e.g. apartment, house, commercial), and any other important criteria they may have for the property search.
    4. Always review the Conversation History to determine if the user's property preferences have already been collected. If they have, respond with the exact phrase 'TERMINATE FLOW' and avoid asking the user for their preferences again.
    5. If any of these details are missing, initiate a friendly dialogue to collect the missed information.
    6. Do not immediately answer property-specific questions without establishing a foundation of user preferences for a more tailored response.
    7. Use collected details to enhance the relevance and personalization of answers.
    8. For questions unrelated to real estate, respond courteously and guide users back to relevant topics.
    9. Always generate **very short**, crisp, precise, polite, generous and real estate professional response. Do not generate lengthy response.
    10. After collecting the user's property preferences, confirm the preferences with the user explicitly. Once the user confirms, respond only with the exact phrase 'TERMINATE FLOW' and nothing else. Do not include any additional text, explanation, or response.

    Example:
    User: Good morning!
    Assistant: Good morning! How can I assist you with your property search today?
    User: Hi
    Assistant: Hello! How can I help you get your desired properties?
    User: Hi, I would like to see some of the properties.
    Assistant: Certainly! Before we proceed, may I have your name?

    Conversation History: {history}
    User: {user_query}
    Assistant:
    """
    
    return prompt


def refine_question(history,user_query):
    history.append({'role': 'user', 'content': user_query})
    prompt=f"""You are a Real Estate helpful assistant who helps user to recommend best properties based on user property preferences. Your task is to refine the final user query based on the conversation history given below: 
    1. Always write the final refine query in english language.
    2. Final refined query must contain all user defined criteria of property preferences from conversation history given.
    3. The final output must be the final refined query. Do not add any extra text.
    """
    chat_completion = client.chat.completions.create(
        messages=[{'role': 'system', 'content': prompt},
                {"role": "user", "content": str(history)}],
        model="llama-3.2-90b-vision-preview",
        temperature=0,
        max_tokens=1024,
    )
    return chat_completion.choices[0].message.content.strip()



def chat(user_query, history):

    res = bot_response(prompt_creation(user_query, history), language='Arabic')
    response=res.replace('"',"")
    # if "terminate flow" in response.lower():

    return res
    