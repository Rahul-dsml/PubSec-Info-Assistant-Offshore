import sqlite3
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq


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
                    3. Always use the wildcard operator `LIKE` for filtering, ensuring all values are transformed to lowercase for consistency. For example, apply filters as `WHERE LOWER(city) LIKE '%pune%'` instead of without converting to lowercase.
                    4. THE RESPONSE MUST BE STRICTLY ONLY THE SQL QUERY. DO NOT INCLUDE ANY TAGS LIKE ```sql``` OR ANY SORT OF EXPLANATIONS. JUST QUERY, AS IT WILL BE DIRECTLY USED IN SQL QUERY ENGINE.
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

    def generate_insight(self, user_query, sql_query, execution_result, chat_language):
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
    df = pd.read_csv(csv_file_path, encoding='latin1')
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
        insight = insight_generator.generate_insight(user_query=user_query,sql_query=generated_sql_query, execution_result=execution_result,chat_language=chat_language)
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




# if __name__ == "__main__":
#     print("------------------------------------++++++++++++++++++++++++++++++++++++++++++++")
#     # user_query = "Recommend me 3 stocks which have average price closer to that of 'Armor Plate Stryker'"
#     user_query = "Hi I am looking for properties in district Summer."
#     csv_file_path = "project_name_district_apartment&unit_type_eng_v3"  # Path to your CSV file
#     sqlite_db_path = "real_estate.db"   # Path to the SQLite database

#     # Call the main function
#     print("Query: ", user_query)
#     insight = main(user_query, csv_file_path, sqlite_db_path)
#     print("Final Insight:", insight)