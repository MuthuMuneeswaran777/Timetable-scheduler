from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session  # type: ignore[reportMissingImports]
from typing import Dict, Any
from sqlalchemy import select  # type: ignore[reportMissingImports]

from backend.database import get_db
from backend.models import Timetable, TimetableEntry, Subject, Teacher, Room, DayOfWeek
from backend.scheduler import generate_timetable

router = APIRouter(prefix="/timetables", tags=["timetables"])


def half_of(period: int) -> str:
	return "AM" if period <= 4 else "PM"


def serialize(obj) -> Dict[str, Any]:
	"""Serialize SQLAlchemy object to dictionary"""
	data = {}
	for col in obj.__table__.columns:
		val = getattr(obj, col.name)
		if hasattr(val, "value"):
			data[col.name] = val.value
		else:
			data[col.name] = val
	return data


@router.get("")
def list_timetables(db: Session = Depends(get_db)):
	try:
		tts = db.query(Timetable).all()
		return [serialize(tt) for tt in tts]
	except Exception as e:
		print(f"Error listing timetables: {e}")
		raise HTTPException(status_code=500, detail=f"Failed to list timetables: {str(e)}")


@router.get("/{tid}")
def get_timetable(tid: int, db: Session = Depends(get_db)):
	try:
		tt = db.query(Timetable).filter(Timetable.timetable_id == tid).first()
		if not tt:
			raise HTTPException(status_code=404, detail="Not found")
		entries = db.query(TimetableEntry).filter(TimetableEntry.timetable_id == tt.timetable_id).all()
		# Enrich names
		sub_map = {s.subject_id: s.subject_name for s in db.query(Subject).all()}
		teacher_map = {t.teacher_id: t.teacher_name for t in db.query(Teacher).all()}
		room_map = {r.room_id: r.room_name for r in db.query(Room).all()}

		return {
			"timetable": serialize(tt),
			"entries": [
				{
					**serialize(e),
					"subject_name": sub_map.get(e.subject_id),
					"teacher_name": teacher_map.get(e.teacher_id),
					"room_name": room_map.get(e.room_id),
					"half_day": half_of(e.period_number),
				}
				for e in entries
			],
		}
	except Exception as e:
		print(f"Error getting timetable {tid}: {e}")
		raise HTTPException(status_code=500, detail=f"Failed to get timetable: {str(e)}")


@router.post("/generate")
def generate(db: Session = Depends(get_db), batch_id: int = 1):
	try:
		print(f"Generating timetable for batch_id: {batch_id}")
		tt = generate_timetable(db, batch_id=batch_id)
		print(f"Generated timetable: {tt.timetable_id}")
		return serialize(tt)
	except Exception as e:
		print(f"Error generating timetable: {e}")
		import traceback
		traceback.print_exc()
		raise HTTPException(status_code=500, detail=f"Failed to generate timetable: {str(e)}")


@router.post("/regenerate/{batch_id}")
def regenerate_timetable(batch_id: int, db: Session = Depends(get_db)):
	"""Regenerate timetable for a batch (deletes existing and creates new)"""
	try:
		# Delete existing timetable for this batch
		existing_tt = db.query(Timetable).filter(Timetable.batch_id == batch_id).first()
		if existing_tt:
			# Delete all entries first
			db.query(TimetableEntry).filter(TimetableEntry.timetable_id == existing_tt.timetable_id).delete()
			# Delete the timetable
			db.delete(existing_tt)
			db.commit()
		
		# Generate new timetable
		tt = generate_timetable(db, batch_id=batch_id)
		return {"message": "Timetable regenerated successfully", "timetable": serialize(tt)}
	except Exception as e:
		print(f"Error regenerating timetable: {e}")
		import traceback
		traceback.print_exc()
		db.rollback()
		raise HTTPException(status_code=500, detail=f"Failed to regenerate timetable: {str(e)}")


@router.delete("/{timetable_id}")
def delete_timetable(timetable_id: int, db: Session = Depends(get_db)):
	"""Delete a timetable and all its entries"""
	tt = db.get(Timetable, timetable_id)
	if not tt:
		raise HTTPException(status_code=404, detail="Timetable not found")
	
	# Delete all entries first
	db.query(TimetableEntry).filter(TimetableEntry.timetable_id == timetable_id).delete()
	# Delete the timetable
	db.delete(tt)
	db.commit()
	return {"message": "Timetable deleted successfully"}


@router.patch("/update/{entry_id}")
def update_entry(entry_id: int, payload: Dict[str, Any], db: Session = Depends(get_db)):
	entry = db.get(TimetableEntry, entry_id)
	if not entry:
		raise HTTPException(status_code=404, detail="Not found")

	new_day = payload.get("day_of_week", entry.day_of_week)
	new_period = payload.get("period_number", entry.period_number)

	# Validate half-day separation for the same subject within a day
	if entry.subject_id is not None:
		conflict = db.scalars(
			select(TimetableEntry)
			.where(
				TimetableEntry.timetable_id == entry.timetable_id,
				TimetableEntry.day_of_week == new_day,
				TimetableEntry.subject_id == entry.subject_id,
			)
		).all()
		for e in conflict:
			if e.entry_id == entry.entry_id:
				continue
			if half_of(e.period_number) == half_of(new_period):
				raise HTTPException(status_code=400, detail="Subject already scheduled in this half-day. Pick the other half.")

	# Validate lab cross-batch half-day conflict for same teacher
	if entry.teacher_id is not None and entry.subject_id is not None:
		sub = db.get(Subject, entry.subject_id)
		if sub and sub.is_lab:
			other = db.scalars(
				select(TimetableEntry)
				.join(Timetable)
				.where(
					Timetable.batch_id != db.get(Timetable, entry.timetable_id).batch_id,
					TimetableEntry.teacher_id == entry.teacher_id,
					TimetableEntry.day_of_week == new_day,
				)
			).all()
			for e in other:
				other_sub = db.get(Subject, e.subject_id) if e.subject_id else None
				if other_sub and other_sub.is_lab and half_of(e.period_number) == half_of(new_period):
					raise HTTPException(status_code=400, detail="This teacher has a lab in the same half-day for another class.")

	# Validate teacher availability
	if entry.teacher_id is not None:
		busy = db.scalars(
			select(TimetableEntry)
			.where(
				TimetableEntry.entry_id != entry.entry_id,
				TimetableEntry.teacher_id == entry.teacher_id,
				TimetableEntry.day_of_week == new_day,
				TimetableEntry.period_number == new_period,
			)
		).first()
		if busy:
			raise HTTPException(status_code=400, detail="Teacher is busy this period.")

	setattr(entry, "day_of_week", new_day)
	setattr(entry, "period_number", new_period)
	db.commit()
	db.refresh(entry)
	return serialize(entry)


def serialize(obj):
	data = {}
	for col in obj.__table__.columns:  # type: ignore[attr-defined]
		val = getattr(obj, col.name)
		try:
			data[col.name] = val.value if hasattr(val, "value") else val
		except Exception:
			data[col.name] = str(val)
	return data
