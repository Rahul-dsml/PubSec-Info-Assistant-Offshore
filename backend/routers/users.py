from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.responses import JSONResponse
from approaches.agent import  refine_question,CodeGeneratorAgent,CodeExecutorAgent,InsightGeneratorAgent,Decision_Agent
from utility.chat_helper import DataDictionaryPrompt
# from approaches.realassistant import main
from model import ChatResponse
from langchain_groq import ChatGroq
import ast

router = APIRouter(prefix="/users", tags=["Users"])


model = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key="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"
    # other params...
)



@router.post("/assistant_chat/")
async def assistant_chat(response:ChatResponse):
    user_query= response.user_query
    chat_history=response.chat_history
    chat_language=response.chat_language
    dict_obj=DataDictionaryPrompt()
    dict_prompt=dict_obj.get_prompt()
    flag_list=["Yes" for i in chat_history if i['content']['SQL_QUERY']=="Yes"]
    flag=len(flag_list)==0
    for chat in chat_history:
        if 'Response' in chat['content']:
            chat['content'] = chat['content']['Response']
            if "lat_long_details_list" in chat:
                del chat["lat_long_details_list"]

    print("------------------------------------------------------------")
    print(chat_history)
    print("-----------------------------------------------------------")
    if flag: # True
        response = Decision_Agent(user_query=user_query, language=chat_language,history=chat_history)
        response = ast.literal_eval(response)
        # response["data"]="NA"
        print("--------------------------------------------------------")

        # print(chat_history)
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
            execution_result,lat_long_details_list = code_executor.execute_sql_query(generated_sql_query)
        
            print("--------------------------------------")
            print(execution_result)
            
            # Step 5: Generate insights from the execution result (Agent C)
            insight = insight_generator.generate_insight(user_query=user_query, sql_query=generated_sql_query, execution_result=execution_result,chat_language=chat_language)
            print("Generated insight:",insight)
            response={"SQL_QUERY":"Yes","Response":insight,"lat_long_details_list":lat_long_details_list}
            
    else:
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
        execution_result,lat_long_details_list = code_executor.execute_sql_query(generated_sql_query)
        print("--------------------------------------")
        print(execution_result)
        
        # Step 5: Generate insights from the execution result (Agent C)
        insight = insight_generator.generate_insight(user_query=user_query, sql_query=generated_sql_query, execution_result=execution_result,chat_language=chat_language)
        print("Generated insight:",insight)
        response={"SQL_QUERY":"Yes","Response":insight,"lat_long_details_list":lat_long_details_list}

    print("-----------------------Final Response------------------------")
    print(response)
    return JSONResponse(content=response, status_code=200)
    # print("User Question ::",user_query)
    # print("Chat History ::",chat_history)
    # print("User Question ::",chat_language)
