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
from backend.routers.auth import router as auth_router

app = FastAPI()

# CORS configuration - allow all origins for development
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],  # Allow all origins for development
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Create tables if not exist (dev convenience)
Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
	return {"message": "Hello from FastAPI 🎉"}


app.include_router(auth_router)
app.include_router(data_router)
app.include_router(timetables_router)

@app.get("/health")
def health_check():
	return {"status": "healthy", "message": "Backend is running!"}

@app.get("/test-rooms")
def test_rooms():
	"""Test endpoint to debug room issues"""
	try:
		import sqlite3
		import os
		
		# Direct database connection
		db_path = os.path.join(os.path.dirname(__file__), "dev.db")
		conn = sqlite3.connect(db_path)
		cursor = conn.cursor()
		
		cursor.execute("SELECT room_id, room_name, capacity, room_type, assigned_batch_id FROM rooms")
		rows = cursor.fetchall()
		
		result = []
		for row in rows:
			result.append({
				"room_id": row[0],
				"room_name": row[1],
				"capacity": row[2],
				"room_type": row[3],
				"assigned_batch_id": row[4]
			})
		
		conn.close()
		return {"rooms": result, "count": len(result), "method": "direct_sqlite"}
	except Exception as e:
		import traceback
		return {"error": str(e), "traceback": traceback.format_exc()}
