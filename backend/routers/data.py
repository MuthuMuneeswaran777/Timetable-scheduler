from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.database import get_db
from backend.models.models import Batch, Teacher, Subject, Room, SubjectOffering

router = APIRouter(prefix="/data", tags=["data"])

EntityName = Literal["batches", "teachers", "subjects", "rooms", "subject_offerings"]
MODEL_MAP = {
    "batches": Batch,
    "teachers": Teacher,
    "subjects": Subject,
    "rooms": Room,
    "subject_offerings": SubjectOffering,
}


class EntityPayload(BaseModel):
	batch_name: Optional[str] = None
	department: Optional[str] = None
	sem: Optional[str] = None
	academic_year: Optional[str] = None

	teacher_name: Optional[str] = None
	email: Optional[str] = None
	max_sessions_per_day: Optional[int] = None
	max_sessions_per_week: Optional[int] = None

	subject_name: Optional[str] = None
	teacher_id: Optional[int] = None
	sessions_per_week: Optional[int] = None
	max_sessions_per_day: Optional[int] = None
	is_lab: Optional[bool] = None
	lab_duration: Optional[int] = None

	room_name: Optional[str] = None
	capacity: Optional[int] = None
	room_type: Optional[str] = None
	assigned_batch_id: Optional[int] = None

	# SubjectOffering fields
	offering_id: Optional[int] = None
	subject_id: Optional[int] = None
	teacher_id: Optional[int] = None
	batch_id: Optional[int] = None
	priority: Optional[int] = None


@router.get("/{entity}")
def list_entities(entity: EntityName, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
	try:
		if entity == "rooms":
			# Direct SQL approach for rooms to bypass ORM issues
			import sqlite3
			import os
			
			db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dev.db")
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
			return result
		else:
			# Use direct SQL for all entities to avoid ORM issues
			import sqlite3
			import os
			
			db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dev.db")
			conn = sqlite3.connect(db_path)
			cursor = conn.cursor()
			
			if entity == "batches":
				cursor.execute("SELECT batch_id, batch_name, department, sem, academic_year FROM batches")
				rows = cursor.fetchall()
				result = []
				for row in rows:
					result.append({
						"batch_id": row[0],
						"batch_name": row[1],
						"department": row[2],
						"sem": row[3],
						"academic_year": row[4]
					})
			elif entity == "teachers":
				cursor.execute("SELECT teacher_id, teacher_name, email, max_sessions_per_day, max_sessions_per_week FROM teachers")
				rows = cursor.fetchall()
				result = []
				for row in rows:
					result.append({
						"teacher_id": row[0],
						"teacher_name": row[1],
						"email": row[2],
						"max_sessions_per_day": row[3],
						"max_sessions_per_week": row[4]
					})
			elif entity == "subjects":
				cursor.execute("SELECT subject_id, subject_name, teacher_id, sessions_per_week, is_lab FROM subjects")
				rows = cursor.fetchall()
				result = []
				for row in rows:
					result.append({
						"subject_id": row[0],
						"subject_name": row[1],
						"teacher_id": row[2],
						"sessions_per_week": row[3],
						"is_lab": bool(row[4])
					})
			elif entity == "subject_offerings":
				cursor.execute("SELECT offering_id, subject_id, teacher_id, batch_id, sessions_per_week, max_sessions_per_day, priority FROM subject_offerings")
				rows = cursor.fetchall()
				result = []
				for row in rows:
					result.append({
						"offering_id": row[0],
						"subject_id": row[1],
						"teacher_id": row[2],
						"batch_id": row[3],
						"sessions_per_week": row[4],
						"max_sessions_per_day": row[5],
						"priority": row[6]
					})
			else:
				result = []
			
			conn.close()
			return result
	except Exception as e:
		import traceback
		error_details = traceback.format_exc()
		print(f"Error listing {entity}: {str(e)}")
		print(f"Traceback: {error_details}")
		raise HTTPException(status_code=500, detail=f"Failed to list {entity}: {str(e)}")


@router.post("/{entity}")
def create_entity(entity: EntityName, payload: EntityPayload, db: Session = Depends(get_db)) -> Dict[str, Any]:
	try:
		payload_data = payload.dict(exclude_unset=True)
		
		# Handle null values for foreign keys
		if "assigned_batch_id" in payload_data and payload_data["assigned_batch_id"] == "":
			payload_data["assigned_batch_id"] = None
		
		if entity == "rooms":
			# Direct SQL approach for rooms
			import sqlite3
			import os
			
			db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dev.db")
			conn = sqlite3.connect(db_path)
			cursor = conn.cursor()
			
			cursor.execute("""
				INSERT INTO rooms (room_name, capacity, room_type, assigned_batch_id) 
				VALUES (?, ?, ?, ?)
			""", (
				payload_data.get("room_name"),
				payload_data.get("capacity"),
				payload_data.get("room_type"),
				payload_data.get("assigned_batch_id")
			))
			
			room_id = cursor.lastrowid
			conn.commit()
			
			# Fetch the created room
			cursor.execute("SELECT room_id, room_name, capacity, room_type, assigned_batch_id FROM rooms WHERE room_id = ?", (room_id,))
			row = cursor.fetchone()
			conn.close()
			
			return {
				"room_id": row[0],
				"room_name": row[1],
				"capacity": row[2],
				"room_type": row[3],
				"assigned_batch_id": row[4]
			}
		else:
			# Use direct SQL for all entities
			import sqlite3
			import os
			
			db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dev.db")
			conn = sqlite3.connect(db_path)
			cursor = conn.cursor()
			
			if entity == "teachers":
				cursor.execute("""
					INSERT INTO teachers (teacher_name, email, max_sessions_per_day, max_sessions_per_week) 
					VALUES (?, ?, ?, ?)
				""", (
					payload_data.get("teacher_name"),
					payload_data.get("email"),
					payload_data.get("max_sessions_per_day", 3),
					payload_data.get("max_sessions_per_week", 15)
				))
				teacher_id = cursor.lastrowid
				conn.commit()
				cursor.execute("SELECT teacher_id, teacher_name, email, max_sessions_per_day, max_sessions_per_week FROM teachers WHERE teacher_id = ?", (teacher_id,))
				row = cursor.fetchone()
				result = {
					"teacher_id": row[0],
					"teacher_name": row[1],
					"email": row[2],
					"max_sessions_per_day": row[3],
					"max_sessions_per_week": row[4]
				}
			elif entity == "subjects":
				# Support additional columns if present in schema
				columns = ["subject_name", "teacher_id", "sessions_per_week", "is_lab"]
				values = [
					payload_data.get("subject_name"),
					payload_data.get("teacher_id"),
					payload_data.get("sessions_per_week", 3),
					payload_data.get("is_lab", False),
				]
				
				# Optionals if table has them (to avoid NOT NULL constraint failures)
				if "max_sessions_per_day" in payload_data:
					columns.append("max_sessions_per_day")
					values.append(payload_data.get("max_sessions_per_day"))
				if "lab_duration" in payload_data:
					columns.append("lab_duration")
					values.append(payload_data.get("lab_duration"))
				
				placeholders = ", ".join(["?"] * len(columns))
				cursor.execute(f"""
					INSERT INTO subjects ({', '.join(columns)}) 
					VALUES ({placeholders})
				""", values)
				subject_id = cursor.lastrowid
				conn.commit()
				cursor.execute("SELECT subject_id, subject_name, teacher_id, sessions_per_week, is_lab FROM subjects WHERE subject_id = ?", (subject_id,))
				row = cursor.fetchone()
				result = {
					"subject_id": row[0],
					"subject_name": row[1],
					"teacher_id": row[2],
					"sessions_per_week": row[3],
					"is_lab": bool(row[4])
				}
			elif entity == "subject_offerings":
				cursor.execute("""
					INSERT INTO subject_offerings (subject_id, teacher_id, batch_id, sessions_per_week, max_sessions_per_day, priority) 
					VALUES (?, ?, ?, ?, ?, ?)
				""", (
					payload_data.get("subject_id"),
					payload_data.get("teacher_id"),
					payload_data.get("batch_id"),
					payload_data.get("sessions_per_week", 3),
					payload_data.get("max_sessions_per_day", 2),
					payload_data.get("priority", 1)
				))
				offering_id = cursor.lastrowid
				conn.commit()
				cursor.execute("SELECT offering_id, subject_id, teacher_id, batch_id, sessions_per_week, max_sessions_per_day, priority FROM subject_offerings WHERE offering_id = ?", (offering_id,))
				row = cursor.fetchone()
				result = {
					"offering_id": row[0],
					"subject_id": row[1],
					"teacher_id": row[2],
					"batch_id": row[3],
					"sessions_per_week": row[4],
					"max_sessions_per_day": row[5],
					"priority": row[6]
				}
			elif entity == "batches":
				cursor.execute("""
					INSERT INTO batches (batch_name, department, sem, academic_year) 
					VALUES (?, ?, ?, ?)
				""", (
					payload_data.get("batch_name"),
					payload_data.get("department"),
					payload_data.get("sem"),
					payload_data.get("academic_year")
				))
				batch_id = cursor.lastrowid
				conn.commit()
				cursor.execute("SELECT batch_id, batch_name, department, sem, academic_year FROM batches WHERE batch_id = ?", (batch_id,))
				row = cursor.fetchone()
				result = {
					"batch_id": row[0],
					"batch_name": row[1],
					"department": row[2],
					"sem": row[3],
					"academic_year": row[4]
				}
			else:
				result = {"error": f"Unsupported entity: {entity}"}
			
			conn.close()
			return result
	except Exception as e:
		import traceback
		print(f"Error creating {entity}: {str(e)}")
		print(f"Traceback: {traceback.format_exc()}")
		db.rollback()
		raise HTTPException(status_code=500, detail=f"Failed to create {entity}: {str(e)}")


@router.put("/{entity}/{item_id}")
def update_entity(entity: EntityName, item_id: int, payload: EntityPayload, db: Session = Depends(get_db)) -> Dict[str, Any]:
	try:
		payload_data = payload.dict(exclude_unset=True)
		
		# Handle null values for foreign keys
		if "assigned_batch_id" in payload_data and (payload_data["assigned_batch_id"] == "" or payload_data["assigned_batch_id"] == "null"):
			payload_data["assigned_batch_id"] = None
		
		if entity == "rooms":
			# Direct SQL approach for rooms
			import sqlite3
			import os
			
			db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dev.db")
			conn = sqlite3.connect(db_path)
			cursor = conn.cursor()
			
			# Check if room exists
			cursor.execute("SELECT room_id FROM rooms WHERE room_id = ?", (item_id,))
			if not cursor.fetchone():
				conn.close()
				raise HTTPException(status_code=404, detail=f"Room with id {item_id} not found")
			
			# Build update query dynamically
			update_fields = []
			update_values = []
			
			if "room_name" in payload_data:
				update_fields.append("room_name = ?")
				update_values.append(payload_data["room_name"])
			if "capacity" in payload_data:
				update_fields.append("capacity = ?")
				update_values.append(payload_data["capacity"])
			if "room_type" in payload_data:
				update_fields.append("room_type = ?")
				update_values.append(payload_data["room_type"])
			if "assigned_batch_id" in payload_data:
				update_fields.append("assigned_batch_id = ?")
				update_values.append(payload_data["assigned_batch_id"])
			
			if update_fields:
				update_values.append(item_id)
				cursor.execute(f"UPDATE rooms SET {', '.join(update_fields)} WHERE room_id = ?", update_values)
				conn.commit()
			
			# Fetch updated room
			cursor.execute("SELECT room_id, room_name, capacity, room_type, assigned_batch_id FROM rooms WHERE room_id = ?", (item_id,))
			row = cursor.fetchone()
			conn.close()
			
			return {
				"room_id": row[0],
				"room_name": row[1],
				"capacity": row[2],
				"room_type": row[3],
				"assigned_batch_id": row[4]
			}
		else:
			# Regular handling for other entities
			Model = MODEL_MAP[entity]
			instance = db.get(Model, item_id)
			if not instance:
				raise HTTPException(status_code=404, detail=f"{entity} with id {item_id} not found")
			
			valid_fields = {col.name for col in Model.__table__.columns}
			for k, v in payload_data.items():
				if k in valid_fields:
					if k.endswith("_id") and v == "":
						v = None
					setattr(instance, k, v)
			
			db.commit()
			db.refresh(instance)
			return serialize(instance)
		
	except Exception as e:
		db.rollback()
		import traceback
		print(f"Error updating {entity} {item_id}: {str(e)}")
		print(f"Traceback: {traceback.format_exc()}")
		raise HTTPException(status_code=500, detail=f"Failed to update {entity}: {str(e)}")


@router.delete("/{entity}/{item_id}")
def delete_entity(entity: EntityName, item_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
	try:
		if entity == "rooms":
			# Direct SQL approach for rooms
			import sqlite3
			import os
			
			db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dev.db")
			conn = sqlite3.connect(db_path)
			cursor = conn.cursor()
			
			# Check if room exists
			cursor.execute("SELECT room_id FROM rooms WHERE room_id = ?", (item_id,))
			if not cursor.fetchone():
				conn.close()
				raise HTTPException(status_code=404, detail=f"Room with id {item_id} not found")
			
			# Delete the room
			cursor.execute("DELETE FROM rooms WHERE room_id = ?", (item_id,))
			conn.commit()
			conn.close()
			
			return {"ok": True}
		else:
			# Use direct SQL for all entities to avoid ORM issues
			import sqlite3
			import os
			
			db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dev.db")
			conn = sqlite3.connect(db_path)
			cursor = conn.cursor()
			
			# Map entity to table name and primary key
			table_config = {
				"batches": ("batches", "batch_id"),
				"teachers": ("teachers", "teacher_id"),
				"subjects": ("subjects", "subject_id"),
				"subject_offerings": ("subject_offerings", "offering_id"),
			}
			
			if entity not in table_config:
				conn.close()
				raise HTTPException(status_code=400, detail=f"Unsupported entity: {entity}")
			
			table_name, id_column = table_config[entity]
			
			# Check if record exists
			cursor.execute(f"SELECT {id_column} FROM {table_name} WHERE {id_column} = ?", (item_id,))
			if not cursor.fetchone():
				conn.close()
				raise HTTPException(status_code=404, detail=f"{entity} with id {item_id} not found")
			
			# Delete the record
			cursor.execute(f"DELETE FROM {table_name} WHERE {id_column} = ?", (item_id,))
			conn.commit()
			conn.close()
			
			return {"ok": True}
	except Exception as e:
		import traceback
		print(f"Error deleting {entity} {item_id}: {str(e)}")
		print(f"Traceback: {traceback.format_exc()}")
		raise HTTPException(status_code=500, detail=f"Failed to delete {entity}: {str(e)}")


def serialize(obj) -> Dict[str, Any]:
	data = {}
	for col in obj.__table__.columns:  # type: ignore[attr-defined]
		val = getattr(obj, col.name)
		if hasattr(val, "value"):
			data[col.name] = val.value
		else:
			data[col.name] = val
	return data
