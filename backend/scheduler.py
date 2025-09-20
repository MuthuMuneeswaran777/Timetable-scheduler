from typing import List, Dict, Tuple, Set, Optional
from sqlalchemy.orm import Session  # type: ignore[reportMissingImports]
from datetime import datetime
import random
from collections import defaultdict

from backend.models import Timetable, TimetableEntry, Subject, Teacher, Room, SubjectOffering, DayOfWeek

DAYS = [DayOfWeek.Mon, DayOfWeek.Tue, DayOfWeek.Wed, DayOfWeek.Thu, DayOfWeek.Fri]
PERIODS = list(range(1, 9))
MORNING_PERIODS = [1, 2, 3, 4]  # Morning session periods
AFTERNOON_PERIODS = [5, 6, 7, 8]  # Afternoon session periods
MORNING_FIRST = 1
AFTERNOON_FIRST = 5


def half_of(period: int) -> str:
	return "AM" if period <= 4 else "PM"


def is_morning(period: int) -> bool:
	return period <= 4


def is_afternoon(period: int) -> bool:
	return period >= 5


class TimetableScheduler:
	def __init__(self, db: Session, batch_id: int):
		self.db = db
		self.batch_id = batch_id
		self.offerings = db.query(SubjectOffering).filter(SubjectOffering.batch_id == batch_id).all()
		self.teachers = db.query(Teacher).all()
		self.rooms = db.query(Room).all()
		
		# Initialize tracking structures
		self.grid: Dict[Tuple[DayOfWeek, int], Optional[Dict]] = {(d, p): None for d in DAYS for p in PERIODS}
		self.global_teacher_schedule: Dict[Tuple[int, DayOfWeek, int], bool] = {}
		self.subject_weekly_count: Dict[int, int] = {}
		self.subject_daily_count: Dict[Tuple[int, DayOfWeek], int] = {}
		self.subject_half_daily_count: Dict[Tuple[int, DayOfWeek, str], int] = {}
		
		# Load existing teacher schedules from all batches
		self._load_existing_schedules()
		
		# Partition rooms
		self.lab_rooms = [r for r in self.rooms if (r.room_type or "").upper().startswith("LAB")]
		self.class_rooms = [r for r in self.rooms if not (r.room_type or "").upper().startswith("LAB")]
		if not self.lab_rooms:
			self.lab_rooms = self.rooms[:1] if self.rooms else []
		if not self.class_rooms:
			self.class_rooms = self.rooms[:1] if self.rooms else []
		
		# Assign rooms to subjects
		self.subject_room_map = self._assign_subject_rooms()

	def _load_existing_schedules(self):
		"""Load existing teacher schedules from all batches to avoid conflicts"""
		existing_entries = self.db.query(TimetableEntry).join(Timetable).filter(
			Timetable.batch_id != self.batch_id
		).all()
		
		for entry in existing_entries:
			if entry.teacher_id:
				self.global_teacher_schedule[(entry.teacher_id, entry.day_of_week, entry.period_number)] = True

	def _assign_subject_rooms(self) -> Dict[int, int]:
		"""Assign appropriate rooms to subjects"""
		subject_room_map = {}
		for offering in self.offerings:
			subject = offering.subject
			if subject.is_lab and self.lab_rooms:
				subject_room_map[subject.subject_id] = self.lab_rooms[hash(subject.subject_id) % len(self.lab_rooms)].room_id
			elif self.class_rooms:
				subject_room_map[subject.subject_id] = self.class_rooms[hash(subject.subject_id) % len(self.class_rooms)].room_id
			elif self.rooms:
				subject_room_map[subject.subject_id] = self.rooms[0].room_id
		return subject_room_map

	def _is_teacher_available(self, teacher_id: int, day: DayOfWeek, period: int) -> bool:
		"""Check if teacher is available at given time slot"""
		# Check global schedule (other batches)
		if (teacher_id, day, period) in self.global_teacher_schedule:
			return False
		
		# Check current batch schedule
		if self.grid[(day, period)] is not None:
			existing_entry = self.grid[(day, period)]
			if existing_entry and existing_entry.get("teacher_id") == teacher_id:
				return False
		
		return True

	def _can_schedule_subject(self, offering: SubjectOffering, day: DayOfWeek, period: int) -> bool:
		"""Check if subject can be scheduled at given time slot"""
		subject = offering.subject
		subject_id = subject.subject_id
		teacher_id = offering.teacher_id
		
		# Get teacher constraints
		teacher = next((t for t in self.teachers if t.teacher_id == teacher_id), None)
		teacher_max_per_day = teacher.max_sessions_per_day if teacher else 2
		teacher_max_per_week = teacher.max_sessions_per_week if teacher else 10
		
		# Check teacher availability
		if not self._is_teacher_available(teacher_id, day, period):
			return False
		
		# Check if teacher has reached their weekly limit for this subject
		current_teacher_weekly_sessions = self._get_teacher_weekly_sessions(teacher_id)
		if current_teacher_weekly_sessions >= teacher_max_per_week:
			return False
		
		# Check weekly limit for this subject (use user-configured sessions_per_week)
		if self.subject_weekly_count.get(subject_id, 0) >= offering.sessions_per_week:
			return False
		
		# Check daily limit for this subject (use user-configured max_sessions_per_day)
		if self.subject_daily_count.get((subject_id, day), 0) >= offering.max_sessions_per_day:
			return False
		
		# Check teacher's daily limit
		current_teacher_daily_sessions = self._get_teacher_daily_sessions(teacher_id, day)
		if current_teacher_daily_sessions >= teacher_max_per_day:
			return False
		
		# Check half-day separation to avoid consecutive sessions of same subject
		# This ensures better learning distribution and prevents subject fatigue
		half = half_of(period)
		if offering.max_sessions_per_day <= 2:
			# For subjects with max 2 sessions per day: max 1 per half-day (prevents consecutive)
			if self.subject_half_daily_count.get((subject_id, day, half), 0) >= 1:
				return False
		else:
			# For subjects with more sessions per day: distribute evenly across half-days
			max_per_half = max(1, offering.max_sessions_per_day // 2)
			if self.subject_half_daily_count.get((subject_id, day, half), 0) >= max_per_half:
				return False
		
		# Prevent same subject in same period for consecutive days
		if self._has_consecutive_day_conflict(subject_id, day, period):
			return False
		
		return True

	def _get_teacher_weekly_sessions(self, teacher_id: int) -> int:
		"""Count total weekly sessions for a teacher in current grid"""
		count = 0
		for (day, period), entry in self.grid.items():
			if entry and entry.get("teacher_id") == teacher_id:
				count += 1
		return count

	def _get_teacher_daily_sessions(self, teacher_id: int, day: DayOfWeek) -> int:
		"""Count daily sessions for a teacher on a specific day in current grid"""
		count = 0
		for period in PERIODS:
			entry = self.grid.get((day, period))
			if entry and entry.get("teacher_id") == teacher_id:
				count += 1
		return count

	def _has_consecutive_day_conflict(self, subject_id: int, day: DayOfWeek, period: int) -> bool:
		"""Check if subject is already scheduled in same period on consecutive days"""
		day_index = DAYS.index(day)
		
		# Check previous day
		if day_index > 0:
			prev_day = DAYS[day_index - 1]
			if self.grid.get((prev_day, period)) is not None:
				prev_entry = self.grid[(prev_day, period)]
				if prev_entry and prev_entry.get("subject_id") == subject_id:
					return True
		
		# Check next day
		if day_index < len(DAYS) - 1:
			next_day = DAYS[day_index + 1]
			if self.grid.get((next_day, period)) is not None:
				next_entry = self.grid[(next_day, period)]
				if next_entry and next_entry.get("subject_id") == subject_id:
					return True
		
		return False

	def _schedule_entry(self, offering: SubjectOffering, day: DayOfWeek, period: int, is_lab: bool = False, lab_part: int = None):
		"""Schedule a single entry"""
		subject = offering.subject
		subject_id = subject.subject_id
		teacher_id = offering.teacher_id
		room_id = self.subject_room_map.get(subject_id)
		
		# Create entry
		entry_data = {
			"subject_id": subject_id,
			"teacher_id": teacher_id,
			"room_id": room_id,
			"is_lab_session": is_lab,
			"lab_session_part": lab_part
		}
		
		self.grid[(day, period)] = entry_data
		
		# Update tracking
		self.global_teacher_schedule[(teacher_id, day, period)] = True
		self.subject_weekly_count[subject_id] = self.subject_weekly_count.get(subject_id, 0) + 1
		self.subject_daily_count[(subject_id, day)] = self.subject_daily_count.get((subject_id, day), 0) + 1
		half = half_of(period)
		self.subject_half_daily_count[(subject_id, day, half)] = self.subject_half_daily_count.get((subject_id, day, half), 0) + 1

	def _schedule_first_periods(self):
		"""Schedule first periods of morning and afternoon with subjects"""
		for day in DAYS:
			# Morning first period
			for offering in self.offerings:
				if offering.subject.is_lab:
					continue  # Labs are scheduled separately
				if self._can_schedule_subject(offering, day, MORNING_FIRST):
					self._schedule_entry(offering, day, MORNING_FIRST)
					break
			
			# Afternoon first period
			for offering in self.offerings:
				if offering.subject.is_lab:
					continue  # Labs are scheduled separately
				if self._can_schedule_subject(offering, day, AFTERNOON_FIRST):
					self._schedule_entry(offering, day, AFTERNOON_FIRST)
					break

	def _get_lab_time_slots(self):
		"""Get all possible lab time slots prioritized by preference"""
		time_slots = []
		
		# Priority order: Try current day first, then other days
		# For each day, try morning first, then afternoon
		for day in DAYS:
			# Morning slots (periods 2-4) - preferred
			time_slots.append((day, 2, "morning", 1))  # Priority 1 (highest)
			# Afternoon slots (periods 6-8) - secondary
			time_slots.append((day, 6, "afternoon", 2))  # Priority 2
		
		# Sort by priority (lower number = higher priority)
		time_slots.sort(key=lambda x: x[3])
		return time_slots

	def _schedule_labs(self):
		"""Schedule lab sessions as 3 continuous periods with intelligent conflict resolution"""
		lab_offerings = [o for o in self.offerings if o.subject.is_lab]
		
		for offering in lab_offerings:
			subject = offering.subject
			lab_duration = subject.lab_duration or 3
			placed = False
			
			# Get all possible time slots in priority order
			time_slots = self._get_lab_time_slots()
			
			for day, start_period, session_type, priority in time_slots:
				if placed:
					break
					
				slots = [(day, start_period + i) for i in range(lab_duration)]
				
				# Check if all slots are available
				can_place = True
				max_period = 4 if session_type == "morning" else 8
				conflict_reason = ""
				
				for slot_day, slot_period in slots:
					if slot_period > max_period:  # Don't exceed session boundary
						can_place = False
						conflict_reason = f"exceeds {session_type} session boundary"
						break
					if not self._is_teacher_available(offering.teacher_id, slot_day, slot_period):
						can_place = False
						conflict_reason = f"teacher {offering.teacher_id} not available at {slot_day.value} period {slot_period}"
						break
					if self.grid[(slot_day, slot_period)] is not None:
						can_place = False
						conflict_reason = f"slot {slot_day.value} period {slot_period} already occupied"
						break
				
				if can_place:
					# Place the lab
					for i, (slot_day, slot_period) in enumerate(slots):
						self._schedule_entry(offering, slot_day, slot_period, is_lab=True, lab_part=i+1)
					placed = True
					print(f"✅ Scheduled lab {subject.subject_name} for batch {self.batch_id} on {day.value} {session_type} (periods {start_period}-{start_period+lab_duration-1})")
					break
				else:
					print(f"⏭️ Skipping {day.value} {session_type} for lab {subject.subject_name} (batch {self.batch_id}): {conflict_reason}")
			
			if not placed:
				print(f"❌ Could not schedule lab {subject.subject_name} for batch {self.batch_id} - no available time slots found")
				# Try to find alternative solutions
				self._suggest_lab_alternatives(offering)

	def _suggest_lab_alternatives(self, offering: SubjectOffering):
		"""Suggest alternative scheduling options for failed lab placement"""
		subject = offering.subject
		teacher_id = offering.teacher_id
		
		print(f"🔍 Analyzing alternatives for lab {subject.subject_name} (batch {self.batch_id}):")
		
		# Check teacher availability across all time slots
		available_slots = []
		time_slots = self._get_lab_time_slots()
		
		for day, start_period, session_type, priority in time_slots:
			lab_duration = subject.lab_duration or 3
			slots = [(day, start_period + i) for i in range(lab_duration)]
			max_period = 4 if session_type == "morning" else 8
			
			# Check if teacher would be available (ignoring current batch conflicts)
			teacher_available = True
			for slot_day, slot_period in slots:
				if slot_period > max_period:
					teacher_available = False
					break
				if (teacher_id, slot_day, slot_period) in self.global_teacher_schedule:
					teacher_available = False
					break
			
			if teacher_available:
				available_slots.append((day, session_type, start_period))
		
		if available_slots:
			print(f"   💡 Teacher is available during: {', '.join([f'{day.value} {session}' for day, session, _ in available_slots])}")
			print(f"   💡 Consider rescheduling other subjects to make room for this lab")
		else:
			print(f"   ⚠️ Teacher {teacher_id} has no available 3-hour blocks this week")
			print(f"   💡 Consider assigning a different teacher or splitting the lab into shorter sessions")

	def _fill_remaining_slots(self):
		"""Fill remaining slots with regular subjects, prioritizing subjects that need more sessions"""
		regular_offerings = [o for o in self.offerings if not o.subject.is_lab]
		
		# Multiple passes to ensure all requested sessions are scheduled
		max_passes = 3
		for pass_num in range(max_passes):
			print(f"   📋 Pass {pass_num + 1}: Scheduling remaining sessions...")
			
			# Sort offerings by how many more sessions they need (priority to under-scheduled subjects)
			offerings_with_deficit = []
			for offering in regular_offerings:
				current_sessions = self.subject_weekly_count.get(offering.subject.subject_id, 0)
				needed_sessions = offering.sessions_per_week - current_sessions
				if needed_sessions > 0:
					offerings_with_deficit.append((offering, needed_sessions))
			
			# Sort by deficit (highest deficit first), then by priority
			offerings_with_deficit.sort(key=lambda x: (-x[1], -x[0].priority))
			
			scheduled_this_pass = False
			
			for day in DAYS:
				for period in PERIODS:
					if self.grid[(day, period)] is not None:
						continue
					
					# Try to schedule a subject that needs more sessions
					for offering, deficit in offerings_with_deficit:
						if self._can_schedule_subject(offering, day, period):
							self._schedule_entry(offering, day, period)
							scheduled_this_pass = True
							print(f"      ✅ Scheduled {offering.subject.subject_name} on {day.value} period {period} (needed {deficit} more sessions)")
							break
			
			# If no subjects were scheduled in this pass, we're done
			if not scheduled_this_pass:
				break
		
		# Report final session counts
		print(f"   📊 Final session counts:")
		for offering in regular_offerings:
			current = self.subject_weekly_count.get(offering.subject.subject_id, 0)
			requested = offering.sessions_per_week
			status = "✅" if current >= requested else "⚠️"
			print(f"      {status} {offering.subject.subject_name}: {current}/{requested} sessions")

	def generate(self) -> Timetable:
		"""Generate the complete timetable"""
		# Create timetable record
		tt = Timetable(batch_id=self.batch_id, generation_date=datetime.utcnow(), status="generated")
		self.db.add(tt)
		self.db.commit()
		self.db.refresh(tt)
		
		if not self.offerings or not self.teachers or not self.rooms:
			return tt
		
		print(f"\n🎯 Generating timetable for batch {self.batch_id}")
		
		# Schedule in order of priority
		self._schedule_first_periods()  # Ensure first periods have subjects
		self._schedule_labs()  # Schedule labs as continuous blocks with conflict resolution
		self._fill_remaining_slots()  # Fill remaining slots
		
		# Persist entries to database
		for day in DAYS:
			for period in PERIODS:
				entry_data = self.grid[(day, period)]
				if entry_data is None:
					continue
				
				entry = TimetableEntry(
					timetable_id=tt.timetable_id,
					subject_id=entry_data.get("subject_id"),
					teacher_id=entry_data.get("teacher_id"),
					room_id=entry_data.get("room_id"),
					day_of_week=day,
					period_number=period,
					is_lab_session=entry_data.get("is_lab_session", False),
					lab_session_part=entry_data.get("lab_session_part")
				)
				self.db.add(entry)
		
		self.db.commit()
		return tt


def generate_timetable(db: Session, batch_id: int) -> Timetable:
	"""Generate timetable for a specific batch"""
	scheduler = TimetableScheduler(db, batch_id)
	return scheduler.generate()
