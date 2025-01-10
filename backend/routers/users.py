from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.responses import JSONResponse
from approaches.agent import bot_response, prompt_creation

from model import ChatResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/assistant_chat/")
async def assistant_chat(response:ChatResponse):
    user_query= response.user_query
    chat_history=response.chat_history
    chat_language=response.chat_language
    response = bot_response(prompt_creation(user_query, chat_history), language=chat_language)
    return JSONResponse(content=response, status_code=200)
    # print("User Question ::",user_query)
    # print("Chat History ::",chat_history)
    # print("User Question ::",chat_language)
