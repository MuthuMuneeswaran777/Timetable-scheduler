from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from backend.database import Base


class DayOfWeek(enum.Enum):
	Mon = "Mon"
	Tue = "Tue"
	Wed = "Wed"
	Thu = "Thu"
	Fri = "Fri"


class Batch(Base):
	__tablename__ = "batches"
	batch_id = Column(Integer, primary_key=True, index=True)
	batch_name = Column(String(100), nullable=False)
	department = Column(String(100), nullable=True)
	sem = Column(String(20), nullable=True)
	academic_year = Column(String(20), nullable=True)

	timetables = relationship("Timetable", back_populates="batch", cascade="all, delete-orphan")
	subject_offerings = relationship("SubjectOffering", back_populates="batch", cascade="all, delete-orphan")


class Teacher(Base):
	__tablename__ = "teachers"
	teacher_id = Column(Integer, primary_key=True, index=True)
	teacher_name = Column(String(100), nullable=False)
	department = Column(String(100), nullable=True)
	email = Column(String(120), unique=True, nullable=False)
	max_sessions_per_day = Column(Integer, default=2, nullable=False)
	max_sessions_per_week = Column(Integer, default=10, nullable=False)

	subjects = relationship("Subject", back_populates="teacher")
	subject_offerings = relationship("SubjectOffering", back_populates="teacher", cascade="all, delete-orphan")


class Subject(Base):
	__tablename__ = "subjects"
	subject_id = Column(Integer, primary_key=True, index=True)
	subject_name = Column(String(120), nullable=False)
	teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"), nullable=True)
	sessions_per_week = Column(Integer, default=5, nullable=False)  # Changed default to 5
	max_sessions_per_day = Column(Integer, default=2, nullable=False)  # New constraint
	is_lab = Column(Boolean, default=False, nullable=False)
	lab_duration = Column(Integer, default=3, nullable=True)  # Duration in periods for labs

	teacher = relationship("Teacher", back_populates="subjects")
	subject_offerings = relationship("SubjectOffering", back_populates="subject", cascade="all, delete-orphan")


class Room(Base):
	__tablename__ = "rooms"
	room_id = Column(Integer, primary_key=True, index=True)
	room_name = Column(String(50), nullable=False)
	capacity = Column(Integer, nullable=True)
	room_type = Column(String(50), nullable=True)  # LAB, CLASSROOM


class SubjectOffering(Base):
	__tablename__ = "subject_offerings"
	offering_id = Column(Integer, primary_key=True, index=True)
	subject_id = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)
	teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"), nullable=False)
	batch_id = Column(Integer, ForeignKey("batches.batch_id"), nullable=False)
	sessions_per_week = Column(Integer, default=5, nullable=False)  # Changed default to 5
	max_sessions_per_day = Column(Integer, default=2, nullable=False)  # New constraint
	priority = Column(Integer, default=1, nullable=False)  # Priority for scheduling

	subject = relationship("Subject", back_populates="subject_offerings")
	teacher = relationship("Teacher", back_populates="subject_offerings")
	batch = relationship("Batch", back_populates="subject_offerings")


class Timetable(Base):
	__tablename__ = "timetables"
	timetable_id = Column(Integer, primary_key=True, index=True)
	batch_id = Column(Integer, ForeignKey("batches.batch_id"), nullable=False)
	generation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
	status = Column(String(30), default="generated", nullable=False)

	batch = relationship("Batch", back_populates="timetables")
	entries = relationship("TimetableEntry", back_populates="timetable", cascade="all, delete-orphan")


class TimetableEntry(Base):
	__tablename__ = "timetable_entries"
	entry_id = Column(Integer, primary_key=True, index=True)
	timetable_id = Column(Integer, ForeignKey("timetables.timetable_id"), nullable=False)
	subject_id = Column(Integer, ForeignKey("subjects.subject_id"), nullable=True)
	teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"), nullable=True)
	room_id = Column(Integer, ForeignKey("rooms.room_id"), nullable=True)
	day_of_week = Column(Enum(DayOfWeek), nullable=False)
	period_number = Column(Integer, nullable=False)
	is_lab_session = Column(Boolean, default=False, nullable=False)  # Track lab sessions
	lab_session_part = Column(Integer, nullable=True)  # Part of lab (1, 2, or 3)

	timetable = relationship("Timetable", back_populates="entries")
