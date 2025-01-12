from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.responses import JSONResponse
from approaches.agent import bot_response, prompt_creation, refine_question
from approaches.realassistant import main
from model import ChatResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/assistant_chat/")
async def assistant_chat(response:ChatResponse):
    user_query= response.user_query
    chat_history=response.chat_history
    chat_language=response.chat_language
    response = bot_response(prompt_creation(user_query, chat_history), language=chat_language)
    print(response)
    print("--------------------------------------------------------")
    # print(chat_history)
    if "terminate flow" in response.lower():
        print("terminate flow")
        response=response.lower().replace('terminate flow',"")
        response=response.capitalize()
        # refine question based history
        refined_user_query=refine_question(chat_history,user_query)
        print(refined_user_query)
        csv_file_path = r"C:\Users\rahul\Desktop\Offshore\PubSec-Info-Assistant-Offshore\data\translated_file.csv"  # Path to your CSV file
        sqlite_db_path = r"C:\Users\rahul\Desktop\Offshore\PubSec-Info-Assistant-Offshore\data\real_estate.db"   # Path to the SQLite database
        # sql generator
        # insights generator
        response = main(refined_user_query, csv_file_path, sqlite_db_path,chat_language)

    return JSONResponse(content=response, status_code=200)
    # print("User Question ::",user_query)
    # print("Chat History ::",chat_history)
    # print("User Question ::",chat_language)
