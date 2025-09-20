import { useEffect, useState } from "react";
import { DataAPI } from "../services/api";

const Table = ({ teachers, onEdit, onDelete, loading }) => (
	<div className="overflow-x-auto rounded-lg border bg-white">
		<table className="min-w-full text-sm">
			<thead className="bg-gray-50 text-left">
				<tr>
					<th className="px-4 py-3 font-medium text-gray-600">Name</th>
					<th className="px-4 py-3 font-medium text-gray-600">ID</th>
					<th className="px-4 py-3 font-medium text-gray-600">Email</th>
					<th className="px-4 py-3 font-medium text-gray-600">Max Sessions/Day</th>
					<th className="px-4 py-3 font-medium text-gray-600">Max Sessions/Week</th>
					<th className="px-4 py-3 font-medium text-gray-600">Actions</th>
				</tr>
			</thead>
			<tbody>
				{loading ? (
					<tr><td className="px-4 py-6 text-center" colSpan={6}>Loading…</td></tr>
				) : teachers.length === 0 ? (
					<tr><td className="px-4 py-6 text-center" colSpan={6}>No teachers yet</td></tr>
				) : teachers.map((t) => (
					<tr key={t.teacher_id} className="border-t">
						<td className="px-4 py-3">{t.teacher_name}</td>
						<td className="px-4 py-3">{t.teacher_id}</td>
						<td className="px-4 py-3">{t.email}</td>
						<td className="px-4 py-3">{t.max_sessions_per_day || 2}</td>
						<td className="px-4 py-3">{t.max_sessions_per_week || 10}</td>
						<td className="px-4 py-3">
							<div className="flex gap-2">
								<button 
									className="rounded-md border border-indigo-300 px-3 py-1 text-indigo-600 hover:bg-indigo-50 transition-colors" 
									onClick={() => onEdit(t)}
								>
									Edit
								</button>
								<button 
									className="rounded-md bg-red-600 px-3 py-1 text-white hover:bg-red-700 transition-colors" 
									onClick={() => onDelete(t.teacher_id)}
								>
									Delete
								</button>
							</div>
						</td>
					</tr>
				))}
			</tbody>
		</table>
	</div>
);

const EntityForm = ({ onAdd, onUpdate, editingTeacher, onCancelEdit, busy, error }) => {
	const [name, setName] = useState(editingTeacher?.teacher_name || "");
	const [email, setEmail] = useState(editingTeacher?.email || "");
	const [maxPerDay, setMaxPerDay] = useState(editingTeacher?.max_sessions_per_day?.toString() || "2");
	const [maxPerWeek, setMaxPerWeek] = useState(editingTeacher?.max_sessions_per_week?.toString() || "10");

	// Update form when editing teacher changes
	useEffect(() => {
		if (editingTeacher) {
			setName(editingTeacher.teacher_name || "");
			setEmail(editingTeacher.email || "");
			setMaxPerDay(editingTeacher.max_sessions_per_day?.toString() || "2");
			setMaxPerWeek(editingTeacher.max_sessions_per_week?.toString() || "10");
		} else {
			setName("");
			setEmail("");
			setMaxPerDay("2");
			setMaxPerWeek("10");
		}
	}, [editingTeacher]);

	const nameHint = name.trim().length === 0 ? "Name is required" : "";
	const emailHint = !email.includes("@") ? "Valid email is required" : "";
	const maxDayHint = !/^[1-9]$/.test(maxPerDay) ? "Enter 1-9" : "";
	const maxWeekHint = !/^([1-9]|[1-2][0-9]|30)$/.test(maxPerWeek) ? "Enter 1-30" : "";

	const canSubmit = !nameHint && !emailHint && !maxDayHint && !maxWeekHint && !busy;

	const handleSubmit = (e) => {
		e.preventDefault();
		if (!canSubmit) return;
		
		const payload = {
			teacher_name: name,
			email: email,
			max_sessions_per_day: Number(maxPerDay),
			max_sessions_per_week: Number(maxPerWeek)
		};

		if (editingTeacher) {
			onUpdate(editingTeacher.teacher_id, payload);
		} else {
			onAdd(payload);
		}

		// Reset form if adding new teacher
		if (!editingTeacher) {
			setName("");
			setEmail("");
			setMaxPerDay("2");
			setMaxPerWeek("10");
		}
	};

	return (
		<form onSubmit={handleSubmit} className="space-y-4 rounded-lg border bg-white p-6">
			<div className="flex items-center justify-between">
				<h3 className="text-lg font-medium text-gray-900">
					{editingTeacher ? "Edit Teacher" : "Add New Teacher"}
				</h3>
				{editingTeacher && (
					<button
						type="button"
						onClick={onCancelEdit}
						className="text-gray-400 hover:text-gray-600"
					>
						<svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
						</svg>
					</button>
				)}
			</div>

			<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
				<div>
					<label className="block text-sm font-medium text-gray-700">Teacher Name</label>
					<input 
						className={`mt-1 w-full rounded-md border px-3 py-2 outline-none focus:ring-2 transition-colors ${
							nameHint ? "border-red-500 focus:ring-red-200" : "border-gray-300 focus:ring-indigo-200"
						}`} 
						value={name} 
						onChange={(e) => setName(e.target.value)} 
						placeholder="e.g., Dr. Anita Sharma" 
					/>
					{nameHint && <p className="mt-1 text-xs text-red-600">{nameHint}</p>}
				</div>

				<div>
					<label className="block text-sm font-medium text-gray-700">Email</label>
					<input 
						type="email"
						className={`mt-1 w-full rounded-md border px-3 py-2 outline-none focus:ring-2 transition-colors ${
							emailHint ? "border-red-500 focus:ring-red-200" : "border-gray-300 focus:ring-indigo-200"
						}`} 
						value={email} 
						onChange={(e) => setEmail(e.target.value)} 
						placeholder="teacher@school.edu" 
					/>
					{emailHint && <p className="mt-1 text-xs text-red-600">{emailHint}</p>}
				</div>

				<div>
					<label className="block text-sm font-medium text-gray-700">Max Sessions per Day</label>
					<input 
						type="number"
						min="1"
						max="9"
						className={`mt-1 w-full rounded-md border px-3 py-2 outline-none focus:ring-2 transition-colors ${
							maxDayHint ? "border-red-500 focus:ring-red-200" : "border-gray-300 focus:ring-indigo-200"
						}`} 
						value={maxPerDay} 
						onChange={(e) => setMaxPerDay(e.target.value)} 
						placeholder="2" 
					/>
					{maxDayHint && <p className="mt-1 text-xs text-red-600">{maxDayHint}</p>}
				</div>

				<div>
					<label className="block text-sm font-medium text-gray-700">Max Sessions per Week</label>
					<input 
						type="number"
						min="1"
						max="30"
						className={`mt-1 w-full rounded-md border px-3 py-2 outline-none focus:ring-2 transition-colors ${
							maxWeekHint ? "border-red-500 focus:ring-red-200" : "border-gray-300 focus:ring-indigo-200"
						}`} 
						value={maxPerWeek} 
						onChange={(e) => setMaxPerWeek(e.target.value)} 
						placeholder="10" 
					/>
					{maxWeekHint && <p className="mt-1 text-xs text-red-600">{maxWeekHint}</p>}
				</div>
			</div>

			{error && <p className="text-sm text-red-600 bg-red-50 p-3 rounded-md">{error}</p>}
			
			<div className="flex gap-3 pt-2">
				<button 
					type="submit"
					disabled={!canSubmit} 
					className={`px-6 py-2 rounded-md text-white font-medium transition-colors ${
						canSubmit 
							? "bg-indigo-600 hover:bg-indigo-700" 
							: "bg-gray-300 cursor-not-allowed"
					}`}
				>
					{busy ? "Saving…" : (editingTeacher ? "Update Teacher" : "Add Teacher")}
				</button>
				
				{editingTeacher && (
					<button
						type="button"
						onClick={onCancelEdit}
						className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
					>
						Cancel
					</button>
				)}
			</div>
		</form>
	);
};

export default function TeacherManagement() {
	const [teachers, setTeachers] = useState([]);
	const [loading, setLoading] = useState(true);
	const [busy, setBusy] = useState(false);
	const [error, setError] = useState("");
	const [editingTeacher, setEditingTeacher] = useState(null);

	useEffect(() => {
		DataAPI.list("teachers").then(setTeachers).finally(() => setLoading(false));
	}, []);

	const handleAdd = async (payload) => {
		setBusy(true);
		setError("");
		try {
			const created = await DataAPI.create("teachers", payload);
			setTeachers((prev) => [created, ...prev]);
		} catch (e) {
			setError("Failed to create teacher");
		} finally {
			setBusy(false);
		}
	};

	const handleUpdate = async (id, payload) => {
		setBusy(true);
		setError("");
		try {
			const updated = await DataAPI.update("teachers", id, payload);
			setTeachers((prev) => prev.map(t => t.teacher_id === id ? updated : t));
			setEditingTeacher(null);
		} catch (e) {
			setError("Failed to update teacher");
		} finally {
			setBusy(false);
		}
	};

	const handleDelete = async (id) => {
		if (!confirm("Are you sure you want to delete this teacher?")) return;
		
		setBusy(true);
		setError("");
		try {
			await DataAPI.remove("teachers", id);
			setTeachers((prev) => prev.filter((t) => t.teacher_id !== id));
		} catch (e) {
			setError("Failed to delete teacher");
		} finally {
			setBusy(false);
		}
	};

	const handleEdit = (teacher) => {
		setEditingTeacher(teacher);
		setError("");
	};

	const handleCancelEdit = () => {
		setEditingTeacher(null);
		setError("");
	};

	return (
		<div className="space-y-6">
			<div>
				<h2 className="text-2xl font-bold text-gray-900">Teacher Management</h2>
				<p className="text-gray-600">Manage teachers, their schedules, and session limits</p>
			</div>

			{/* Add/Edit Form */}
			<EntityForm 
				onAdd={handleAdd}
				onUpdate={handleUpdate}
				editingTeacher={editingTeacher}
				onCancelEdit={handleCancelEdit}
				busy={busy} 
				error={error} 
			/>

			{/* Teachers Table */}
			<div>
				<h3 className="text-lg font-medium text-gray-900 mb-4">All Teachers</h3>
				<Table
					teachers={teachers}
					onEdit={handleEdit}
					onDelete={handleDelete}
					loading={loading}
				/>
			</div>
		</div>
	);
}
