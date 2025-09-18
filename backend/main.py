from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

try:
	from dotenv import load_dotenv  # type: ignore
	load_dotenv()
except Exception:
	# Proceed without .env if python-dotenv is not installed
	pass

from backend.database import Base, engine
from backend.models import *  # noqa: F401,F403 to register models
from backend.routers.data import router as data_router
from backend.routers.timetables import router as timetables_router

app = FastAPI()

origins = os.getenv("CORS_ORIGINS", "*").split(",")

# Allow frontend (React) to talk with backend (FastAPI)
app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Create tables if not exist (dev convenience)
Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
	return {"message": "Hello from FastAPI 🎉"}


app.include_router(data_router)
app.include_router(timetables_router)
