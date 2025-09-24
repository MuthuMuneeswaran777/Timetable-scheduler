from typing import List, Dict, Tuple, Set, Optional
from sqlalchemy.orm import Session  # type: ignore[reportMissingImports]
from datetime import datetime
import random
from collections import defaultdict

from ortools.sat.python import cp_model

from backend.models.models import Timetable, TimetableEntry, Subject, Teacher, Room, SubjectOffering, DayOfWeek

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
		
		# Initialize CP-SAT model
		self.model = cp_model.CpModel()
		self.solver = cp_model.CpSolver()
		self.solver.parameters.max_time_in_seconds = 60.0  # 60 second timeout
		
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
		
		# CP-SAT variables and constraints
		self.variables = {}
		self.constraints = []
		self.objective_terms = []

	def _load_existing_schedules(self):
		"""Load existing teacher and room schedules from all batches to avoid conflicts"""
		existing_entries = self.db.query(TimetableEntry).join(Timetable).filter(
			Timetable.batch_id != self.batch_id
		).all()
		
		# Track teacher conflicts
		self.global_teacher_schedule: Dict[Tuple[int, DayOfWeek, int], bool] = {}
		for entry in existing_entries:
			if entry.teacher_id:
				self.global_teacher_schedule[(entry.teacher_id, entry.day_of_week, entry.period_number)] = True
		
		# Track room conflicts (especially important for labs)
		self.global_room_schedule: Dict[Tuple[int, DayOfWeek, int], bool] = {}
		for entry in existing_entries:
			if entry.room_id and entry.is_lab_session:  # Only track lab room conflicts
				self.global_room_schedule[(entry.room_id, entry.day_of_week, entry.period_number)] = True

	def _assign_subject_rooms(self) -> Dict[int, int]:
		"""Assign appropriate rooms to subjects with batch-specific allocation"""
		subject_room_map = {}
		
		# Get batch-assigned rooms first
		batch_assigned_rooms = [r for r in self.rooms if r.assigned_batch_id == self.batch_id]
		batch_lab_rooms = [r for r in batch_assigned_rooms if (r.room_type or "").upper().startswith("LAB")]
		batch_class_rooms = [r for r in batch_assigned_rooms if not (r.room_type or "").upper().startswith("LAB")]
		
		# Fallback to unassigned rooms
		unassigned_rooms = [r for r in self.rooms if r.assigned_batch_id is None]
		unassigned_lab_rooms = [r for r in unassigned_rooms if (r.room_type or "").upper().startswith("LAB")]
		unassigned_class_rooms = [r for r in unassigned_rooms if not (r.room_type or "").upper().startswith("LAB")]
		
		# Combine batch-assigned and unassigned rooms
		available_lab_rooms = batch_lab_rooms + unassigned_lab_rooms
		available_class_rooms = batch_class_rooms + unassigned_class_rooms
		
		# If no specific rooms available, use any available rooms
		if not available_lab_rooms:
			available_lab_rooms = unassigned_rooms[:1] if unassigned_rooms else self.rooms[:1]
		if not available_class_rooms:
			available_class_rooms = unassigned_rooms[:1] if unassigned_rooms else self.rooms[:1]
		
		for offering in self.offerings:
			subject = offering.subject
			if subject.is_lab and available_lab_rooms:
				# For labs, try to assign a consistent room to avoid conflicts
				room_index = hash(f"{self.batch_id}_{subject.subject_id}") % len(available_lab_rooms)
				subject_room_map[subject.subject_id] = available_lab_rooms[room_index].room_id
			elif available_class_rooms:
				# For regular classes, assign based on batch and subject
				room_index = hash(f"{self.batch_id}_{subject.subject_id}") % len(available_class_rooms)
				subject_room_map[subject.subject_id] = available_class_rooms[room_index].room_id
			elif self.rooms:
				# Last resort: use any available room
				subject_room_map[subject.subject_id] = self.rooms[0].room_id
				
		return subject_room_map

	def _create_variables(self):
		"""Create CP-SAT variables for each possible assignment"""
		# Variable: x[offering_id][day][period] = 1 if offering is scheduled at (day, period)
		for offering in self.offerings:
			offering_id = offering.offering_id
			self.variables[offering_id] = {}
			for day in DAYS:
				self.variables[offering_id][day] = {}
				for period in PERIODS:
					var_name = f"x_{offering_id}_{day.value}_{period}"
					self.variables[offering_id][day][period] = self.model.NewBoolVar(var_name)

	def _add_hard_constraints(self):
		"""Add hard constraints that must be satisfied"""
		print("🔧 Adding hard constraints...")
		
		# Constraint 1: Each offering must meet its sessions_per_week requirement
		for offering in self.offerings:
			offering_id = offering.offering_id
			sessions_needed = offering.sessions_per_week
			
			# Sum of all time slots for this offering
			session_vars = []
			for day in DAYS:
				for period in PERIODS:
					session_vars.append(self.variables[offering_id][day][period])
			
			# Must have exactly sessions_needed sessions
			self.model.Add(sum(session_vars) == sessions_needed)
			print(f"   ✅ {offering.subject.subject_name}: {sessions_needed} sessions per week")

		# Constraint 2: No teacher can teach two classes at the same time
		for day in DAYS:
			for period in PERIODS:
				# Group offerings by teacher for this time slot
				teacher_offerings = defaultdict(list)
				for offering in self.offerings:
					teacher_offerings[offering.teacher_id].append(offering.offering_id)
				
				# Each teacher can teach at most one class per time slot
				for teacher_id, offering_ids in teacher_offerings.items():
					if len(offering_ids) > 1:
						teacher_vars = [self.variables[oid][day][period] for oid in offering_ids]
						self.model.Add(sum(teacher_vars) <= 1)

		# Constraint 3: No room can be used by two classes at the same time
		for day in DAYS:
			for period in PERIODS:
				# Group offerings by room for this time slot
				room_offerings = defaultdict(list)
				for offering in self.offerings:
					room_id = self.subject_room_map.get(offering.subject.subject_id)
					if room_id:
						room_offerings[room_id].append(offering.offering_id)
				
				# Each room can host at most one class per time slot
				for room_id, offering_ids in room_offerings.items():
					if len(offering_ids) > 1:
						room_vars = [self.variables[oid][day][period] for oid in offering_ids]
						self.model.Add(sum(room_vars) <= 1)

		# Constraint 4: Teacher daily session limits
		for offering in self.offerings:
			teacher = next((t for t in self.teachers if t.teacher_id == offering.teacher_id), None)
			if teacher:
				max_daily = teacher.max_sessions_per_day or 2
				for day in DAYS:
					daily_vars = [self.variables[offering.offering_id][day][period] for period in PERIODS]
					self.model.Add(sum(daily_vars) <= max_daily)

		# Constraint 5: Subject daily session limits
		for offering in self.offerings:
			max_daily = offering.max_sessions_per_day or 2
			for day in DAYS:
				daily_vars = [self.variables[offering.offering_id][day][period] for period in PERIODS]
				self.model.Add(sum(daily_vars) <= max_daily)

		# Constraint 6: First periods must be non-lab subjects
		for day in DAYS:
			for period in [MORNING_FIRST, AFTERNOON_FIRST]:
				lab_vars = []
				for offering in self.offerings:
					if offering.subject.is_lab:
						lab_vars.append(self.variables[offering.offering_id][day][period])
				
				# No lab subjects in first periods
				if lab_vars:
					self.model.Add(sum(lab_vars) == 0)

		# Constraint 7: Lab subjects must be scheduled in continuous 3-period blocks
		for offering in self.offerings:
			if offering.subject.is_lab:
				offering_id = offering.offering_id
				lab_duration = offering.subject.lab_duration or 3
				
				# For each possible starting position, ensure continuity
				for day in DAYS:
					for start_period in PERIODS:
						if start_period + lab_duration - 1 > max(PERIODS):
							continue
						
						# If lab starts at start_period, it must occupy the next lab_duration periods
						start_var = self.variables[offering_id][day][start_period]
						
						# Create implication: if start_var is true, then all subsequent periods must be true
						for i in range(1, lab_duration):
							next_period = start_period + i
							if next_period <= max(PERIODS):
								next_var = self.variables[offering_id][day][next_period]
								# start_var implies next_var
								self.model.Add(next_var >= start_var)

		# Constraint 8: Respect existing teacher schedules (global conflicts)
		for offering in self.offerings:
			offering_id = offering.offering_id
			teacher_id = offering.teacher_id
			
			for day in DAYS:
				for period in PERIODS:
					# If teacher is already scheduled elsewhere, this offering cannot be scheduled
					if (teacher_id, day, period) in self.global_teacher_schedule:
						self.model.Add(self.variables[offering_id][day][period] == 0)

		# Constraint 9: Respect existing room schedules for labs
		for offering in self.offerings:
			if offering.subject.is_lab:
				offering_id = offering.offering_id
				room_id = self.subject_room_map.get(offering.subject.subject_id)
				
				if room_id:
					for day in DAYS:
						for period in PERIODS:
							# If room is already scheduled elsewhere, this lab cannot be scheduled
							if (room_id, day, period) in self.global_room_schedule:
								self.model.Add(self.variables[offering_id][day][period] == 0)

	def _add_soft_constraints(self):
		"""Add soft constraints for optimization objectives"""
		print("🎯 Adding soft constraints for optimization...")
		
		# Objective 1: Minimize teacher idle gaps
		for teacher in self.teachers:
			teacher_offerings = [o for o in self.offerings if o.teacher_id == teacher.teacher_id]
			if not teacher_offerings:
				continue
				
			for day in DAYS:
				# Count gaps between periods for this teacher
				for period in range(1, max(PERIODS)):
					# Gap exists if teacher has class at period but not at period+1
					has_class_now = []
					has_class_next = []
					
					for offering in teacher_offerings:
						has_class_now.append(self.variables[offering.offering_id][day][period])
						has_class_next.append(self.variables[offering.offering_id][day][period + 1])
					
					# Create gap variable
					gap_var = self.model.NewBoolVar(f"gap_{teacher.teacher_id}_{day.value}_{period}")
					
					# Gap exists if has class now but not next
					now_sum = sum(has_class_now)
					next_sum = sum(has_class_next)
					
					# gap_var = 1 if now_sum >= 1 and next_sum == 0
					self.model.Add(gap_var >= now_sum - next_sum)
					self.model.Add(gap_var <= now_sum)
					self.model.Add(gap_var <= 1 - next_sum)
					
					# Minimize gaps (add to objective)
					self.objective_terms.append(gap_var)

		# Objective 2: Balance teacher workload (minimize pairwise differences)
		teacher_to_workload: Dict[int, cp_model.IntVar] = {}
		max_slots = len(DAYS) * len(PERIODS)
		
		# Build an IntVar for each teacher's total assigned sessions and tie it to the sum of their x vars
		for teacher in self.teachers:
			teacher_offerings = [o for o in self.offerings if o.teacher_id == teacher.teacher_id]
			if not teacher_offerings:
				continue
			workload_sum_terms = []
			for offering in teacher_offerings:
				for day in DAYS:
					for period in PERIODS:
						workload_sum_terms.append(self.variables[offering.offering_id][day][period])
			workload_var = self.model.NewIntVar(0, max_slots, f"workload_{teacher.teacher_id}")
			self.model.Add(workload_var == sum(workload_sum_terms))
			teacher_to_workload[teacher.teacher_id] = workload_var
		
		# Add absolute difference vars for each pair of teachers and minimize their sum
		teacher_ids = list(teacher_to_workload.keys())
		for i in range(len(teacher_ids)):
			for j in range(i + 1, len(teacher_ids)):
				wi = teacher_to_workload[teacher_ids[i]]
				wj = teacher_to_workload[teacher_ids[j]]
				diff = self.model.NewIntVar(0, max_slots, f"workload_diff_{teacher_ids[i]}_{teacher_ids[j]}")
				self.model.AddAbsEquality(diff, wi - wj)
				self.objective_terms.append(diff)

		# Objective 3: Maximize room utilization
		for room in self.rooms:
			room_offerings = []
			for offering in self.offerings:
				room_id = self.subject_room_map.get(offering.subject.subject_id)
				if room_id == room.room_id:
					for day in DAYS:
						for period in PERIODS:
							room_offerings.append(self.variables[offering.offering_id][day][period])
			
			if room_offerings:
				# Maximize room usage (minimize negative usage)
				usage_sum = sum(room_offerings)
				neg_usage = self.model.NewIntVar(0, 40, f"neg_room_usage_{room.room_id}")
				self.model.Add(neg_usage >= -usage_sum)
				self.objective_terms.append(neg_usage)

	def _solve(self) -> bool:
		"""Solve the CP-SAT model"""
		print("🚀 Solving with OR-Tools CP-SAT...")
		
		# Set objective to minimize the sum of all objective terms
		if self.objective_terms:
			self.model.Minimize(sum(self.objective_terms))
		
		# Solve
		status = self.solver.Solve(self.model)
		
		if status == cp_model.OPTIMAL:
			print("✅ Found optimal solution!")
			return True
		elif status == cp_model.FEASIBLE:
			print("⚠️ Found feasible solution (not optimal)")
			return True
		else:
			print("❌ No solution found")
			return False

	def _extract_solution(self) -> Dict[Tuple[DayOfWeek, int], Dict]:
		"""Extract the solution from the solver"""
		solution = {}
		
		for offering in self.offerings:
			offering_id = offering.offering_id
			for day in DAYS:
				for period in PERIODS:
					if self.solver.Value(self.variables[offering_id][day][period]) == 1:
						# This offering is scheduled at (day, period)
						room_id = self.subject_room_map.get(offering.subject.subject_id)
						
						entry_data = {
							"subject_id": offering.subject.subject_id,
							"teacher_id": offering.teacher_id,
							"room_id": room_id,
							"is_lab_session": offering.subject.is_lab,
							"lab_session_part": None  # Will be determined later for labs
						}
						
						solution[(day, period)] = entry_data
		
		return solution


	def generate(self) -> Timetable:
		"""Generate the complete timetable using OR-Tools CP-SAT"""
		# Create timetable record
		tt = Timetable(batch_id=self.batch_id, generation_date=datetime.utcnow(), status="generated")
		self.db.add(tt)
		self.db.commit()
		self.db.refresh(tt)
		
		if not self.offerings or not self.teachers or not self.rooms:
			print("⚠️ No offerings, teachers, or rooms available")
			return tt
		
		print(f"\n🎯 Generating timetable for batch {self.batch_id} using OR-Tools CP-SAT")
		print(f"   📊 {len(self.offerings)} offerings, {len(self.teachers)} teachers, {len(self.rooms)} rooms")
		
		# Step 1: Create CP-SAT variables
		self._create_variables()
		print(f"   ✅ Created {sum(len(day_vars) for offering_vars in self.variables.values() for day_vars in offering_vars.values())} variables")
		
		# Step 2: Add hard constraints
		self._add_hard_constraints()
		
		# Step 3: Add soft constraints for optimization
		self._add_soft_constraints()
		
		# Step 4: Solve the model
		if not self._solve():
			print("❌ Failed to find a solution. Consider relaxing constraints or adding more resources.")
			tt.status = "failed"
			self.db.commit()
			return tt
		
		# Step 5: Extract solution
		solution = self._extract_solution()
		print(f"   ✅ Extracted solution with {len(solution)} scheduled entries")
		
		# Step 6: Process lab sessions to add lab_session_part
		solution = self._process_lab_sessions(solution)
		
		# Step 7: Persist entries to database
		entries_created = 0
		for (day, period), entry_data in solution.items():
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
			entries_created += 1
		
		self.db.commit()
		print(f"   ✅ Created {entries_created} timetable entries in database")
		
		# Report solution quality
		self._report_solution_quality(solution)
		
		return tt

	def _process_lab_sessions(self, solution: Dict[Tuple[DayOfWeek, int], Dict]) -> Dict[Tuple[DayOfWeek, int], Dict]:
		"""Process lab sessions to add lab_session_part numbers"""
		# Group lab sessions by subject and day
		lab_sessions = defaultdict(list)
		
		for (day, period), entry_data in solution.items():
			if entry_data.get("is_lab_session"):
				subject_id = entry_data.get("subject_id")
				lab_sessions[(subject_id, day)].append((period, entry_data))
		
		# Assign lab_session_part numbers
		for (subject_id, day), sessions in lab_sessions.items():
			# Sort by period number
			sessions.sort(key=lambda x: x[0])
			
			# Assign part numbers
			for part_num, (period, entry_data) in enumerate(sessions, 1):
				entry_data["lab_session_part"] = part_num
		
		return solution

	def _report_solution_quality(self, solution: Dict[Tuple[DayOfWeek, int], Dict]):
		"""Report the quality of the generated solution"""
		print("\n📊 Solution Quality Report:")
		
		# Count sessions per subject
		subject_sessions = defaultdict(int)
		teacher_sessions = defaultdict(int)
		room_usage = defaultdict(int)
		
		for (day, period), entry_data in solution.items():
			subject_id = entry_data.get("subject_id")
			teacher_id = entry_data.get("teacher_id")
			room_id = entry_data.get("room_id")
			
			if subject_id:
				subject_sessions[subject_id] += 1
			if teacher_id:
				teacher_sessions[teacher_id] += 1
			if room_id:
				room_usage[room_id] += 1
		
		# Report subject sessions
		print("   📚 Subject Sessions:")
		for offering in self.offerings:
			subject_id = offering.subject.subject_id
			scheduled = subject_sessions.get(subject_id, 0)
			required = offering.sessions_per_week
			status = "✅" if scheduled == required else "⚠️"
			print(f"      {status} {offering.subject.subject_name}: {scheduled}/{required} sessions")
		
		# Report teacher workload
		print("   👨‍🏫 Teacher Workload:")
		for teacher in self.teachers:
			sessions = teacher_sessions.get(teacher.teacher_id, 0)
			max_daily = teacher.max_sessions_per_day or 2
			max_weekly = teacher.max_sessions_per_week or 10
			status = "✅" if sessions <= max_weekly else "⚠️"
			print(f"      {status} {teacher.teacher_name}: {sessions} sessions/week (max: {max_weekly})")
		
		# Report room utilization
		print("   🏫 Room Utilization:")
		for room in self.rooms:
			usage = room_usage.get(room.room_id, 0)
			max_possible = len(DAYS) * len(PERIODS)
			utilization = (usage / max_possible) * 100 if max_possible > 0 else 0
			print(f"      📍 {room.room_name}: {usage}/{max_possible} slots ({utilization:.1f}%)")


def generate_timetable(db: Session, batch_id: int) -> Timetable:
	"""Generate timetable for a specific batch"""
	scheduler = TimetableScheduler(db, batch_id)
	return scheduler.generate()
