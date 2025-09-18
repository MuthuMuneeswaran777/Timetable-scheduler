from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.database import get_db
from backend.models import Batch, Teacher, Subject, Room, SubjectOffering

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

	# SubjectOffering fields
	offering_id: Optional[int] = None
	subject_id: Optional[int] = None
	teacher_id: Optional[int] = None
	batch_id: Optional[int] = None
	priority: Optional[int] = None


@router.get("/{entity}")
def list_entities(entity: EntityName, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
	Model = MODEL_MAP[entity]
	records = db.scalars(select(Model)).all()
	return [serialize(record) for record in records]


@router.post("/{entity}")
def create_entity(entity: EntityName, payload: EntityPayload, db: Session = Depends(get_db)) -> Dict[str, Any]:
	Model = MODEL_MAP[entity]
	instance = Model(**payload.dict(exclude_unset=True))
	db.add(instance)
	db.commit()
	db.refresh(instance)
	return serialize(instance)


@router.put("/{entity}/{item_id}")
def update_entity(entity: EntityName, item_id: int, payload: EntityPayload, db: Session = Depends(get_db)) -> Dict[str, Any]:
	Model = MODEL_MAP[entity]
	instance = db.get(Model, item_id)
	if not instance:
		raise HTTPException(status_code=404, detail="Not found")
	for k, v in payload.dict(exclude_unset=True).items():
		setattr(instance, k, v)
	db.commit()
	db.refresh(instance)
	return serialize(instance)


@router.delete("/{entity}/{item_id}")
def delete_entity(entity: EntityName, item_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
	Model = MODEL_MAP[entity]
	instance = db.get(Model, item_id)
	if not instance:
		raise HTTPException(status_code=404, detail="Not found")
	db.delete(instance)
	db.commit()
	return {"ok": True}


def serialize(obj) -> Dict[str, Any]:
	data = {}
	for col in obj.__table__.columns:  # type: ignore[attr-defined]
		val = getattr(obj, col.name)
		if hasattr(val, "value"):
			data[col.name] = val.value
		else:
			data[col.name] = val
	return data
