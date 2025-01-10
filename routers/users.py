from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from model import ChatResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/assistant_chat/")
def chat(response:ChatResponse):
    user_query= response.user_query
    chat_history=response.chat_history
    chat_language=response.chat_language
    print("User Question ::",user_query)
    print("Chat History ::",chat_history)
    print("User Question ::",chat_language)
