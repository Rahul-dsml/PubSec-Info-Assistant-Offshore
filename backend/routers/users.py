from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends,APIRouter
from fastapi.responses import JSONResponse
from utility.agents import (refine_question,
                    CodeGeneratorAgent,
                    CodeExecutorAgent,
                    InsightGeneratorAgent,
                    query_classifier)

from utility.chat_helper import DataDictionaryPrompt
from model import ChatResponse,GetDetails
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import ast
import os
from utility.feedback_reports import Report

router = APIRouter(prefix="/users", tags=["Users"])

load_dotenv()

model = ChatGroq(
    model=os.getenv("MODEL_NAME"),
    temperature=0.1,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.getenv("GROQ_API_KEY"))

@router.post("/assistant_chat/")
async def assistant_chat(response:ChatResponse):
    user_query= response.user_query
    chat_history=response.chat_history
    chat_language=response.chat_language

    dict_obj=DataDictionaryPrompt()
    dict_prompt=dict_obj.get_prompt()

    # flag_list=["Yes" for i in chat_history if i['content']['SQL_QUERY']=="Yes"]

    for chat in chat_history:
        if 'Response' in chat['content']:
            chat['content'] = chat['content']['Response']
            if "lat_long_details_list" in chat:
                del chat["lat_long_details_list"]
    print("------------------------------------------------------------")
    print(chat_history)
    print("-----------------------------------------------------------")
    print("chat_language ::",chat_language)
    
    # Generate response
    agent = InsightGeneratorAgent(llm=model)
    response = agent.generate_insight(user_query=user_query, 
                                    chat_history=chat_history[1:],
                                    chat_language=chat_language)
    # Parse response into dictionary
    response = ast.literal_eval(response)

    if response['SQL_QUERY'].lower() == "yes":
        print("Processing terminate flow logic...")

        query_type = query_classifier(user_query=user_query)
        print(query_type)
        refined_user_query = refine_question(user_query=user_query, 
                                            history=chat_history)
        print(f"Refined Query: {refined_user_query}")

        dict_object = DataDictionaryPrompt()
        dict_prompt = dict_object.get_prompt()

        code_generator = CodeGeneratorAgent(llm=model)
        code_executor = CodeExecutorAgent()

        sql_query = code_generator.generate_sql_query(
            query=refined_user_query,
            dict_prompt=dict_prompt,
            search_based=query_type
        )
        print("Generated SQL Query:")
        print(sql_query)

        result = code_executor.execute_sql_query(sql_query=sql_query)

        print("--- Execution Results ---")
        print(result[0])
        
        insights = agent.generate_insight(
            user_query=user_query, 
            execution_result=result[0], 
            chat_history=chat_history,
            chat_language=chat_language)

        insights = ast.literal_eval(insights)
        response['Response'] = insights['Response']
        response['lat_long_details_list'] = result[1]
        print("Insights:")
        print(insights['Response'])

    return JSONResponse(content=response, status_code=200)

@router.post("/get_details/")
async def get_details(response:GetDetails):
    apartment_id=response.apartment_id
    language = response.language
    report_obj=Report(apartment_id)
    response=report_obj.generate_report(language=language)
    return JSONResponse(content=response, status_code=200)