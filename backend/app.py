import asyncio
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users,setup
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

# Allow specific frontend URL
origins = [
    "https://realestateassistantfrontend.vercel.app",  # Your frontend
    "http://localhost:8000",  # Allow local testing
]

# @asynccontextmanager
async def lifespan(app: FastAPI):
	# Run at startup
	asyncio.create_task(setup.create_service())
	yield
	# Run on shutdown (if required)
	print('It is shutting down...')

app = FastAPI(lifespan=lifespan)

# CORS setup
app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Routers
app.include_router(setup.router)
# app.include_router(auth.router)
app.include_router(users.router)
