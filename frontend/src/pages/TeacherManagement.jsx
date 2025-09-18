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
					<th className="px-4 py-3 font-medium text-gray-600">Actions</th>
				</tr>
			</thead>
			<tbody>
				{loading ? (
					<tr><td className="px-4 py-6 text-center" colSpan={4}>Loading…</td></tr>
				) : teachers.length === 0 ? (
					<tr><td className="px-4 py-6 text-center" colSpan={4}>No teachers yet</td></tr>
				) : teachers.map((t) => (
					<tr key={t.teacher_id} className="border-t">
						<td className="px-4 py-3">{t.teacher_name}</td>
						<td className="px-4 py-3">{t.teacher_id}</td>
						<td className="px-4 py-3">{t.email}</td>
						<td className="px-4 py-3">
							<div className="flex gap-2">
								<button className="rounded-md border px-3 py-1 hover:bg-gray-50" onClick={() => onEdit(t)}>Edit</button>
								<button className="rounded-md bg-red-600 px-3 py-1 text-white hover:opacity-90" onClick={() => onDelete(t.teacher_id)}>Delete</button>
							</div>
						</td>
					</tr>
				))}
			</tbody>
		</table>
	</div>
);

const EntityForm = ({ onAdd, busy, error }) => {
	const [name, setName] = useState("");
	const [subject, setSubject] = useState("");
	const [maxPerDay, setMaxPerDay] = useState("");

	const nameHint = name.trim().length === 0 ? "Name is required" : "";
	const subjectHint = subject.trim().length === 0 ? "Subject is required" : "";
	const maxHint = !/^[1-9]$/.test(maxPerDay) ? "Enter 1-9" : "";

	const canSubmit = !nameHint && !subjectHint && !maxHint && !busy;

	return (
		<form
			onSubmit={(e) => {
				e.preventDefault();
				if (!canSubmit) return;
				onAdd({ teacher_name: name, department: "", email: `${name.toLowerCase().replace(/\s+/g, ".")}@school.edu`, max_sessions_per_day: Number(maxPerDay) });
				setName("");
				setSubject("");
				setMaxPerDay("");
			}}
			className="space-y-3 rounded-lg border bg-white p-4"
		>
			<div>
				<label className="block text-sm font-medium">Name</label>
				<input className={`mt-1 w-full rounded-md border px-3 py-2 outline-none focus:ring-2 ${nameHint ? "border-red-500 focus:ring-red-200" : "border-gray-300 focus:ring-gray-200"}`} value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g., Anita Sharma" />
				{nameHint && <p className="mt-1 text-xs text-red-600">{nameHint}</p>}
			</div>
			<div>
				<label className="block text-sm font-medium">Subject</label>
				<input className={`mt-1 w-full rounded-md border px-3 py-2 outline-none focus:ring-2 ${subjectHint ? "border-red-500 focus:ring-red-200" : "border-gray-300 focus:ring-gray-200"}`} value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="e.g., Math" />
				{subjectHint && <p className="mt-1 text-xs text-red-600">{subjectHint}</p>}
			</div>
			<div>
				<label className="block text-sm font-medium">Max Sessions/Day</label>
				<input className={`mt-1 w-full rounded-md border px-3 py-2 outline-none focus:ring-2 ${maxHint ? "border-red-500 focus:ring-red-200" : "border-gray-300 focus:ring-gray-200"}`} value={maxPerDay} onChange={(e) => setMaxPerDay(e.target.value)} placeholder="1-9" />
				{maxHint && <p className="mt-1 text-xs text-red-600">{maxHint}</p>}
			</div>
			{error && <p className="text-xs text-red-600">{error}</p>}
			<div className="pt-2">
				<button disabled={!canSubmit} className={`rounded-md px-4 py-2 text-white ${canSubmit ? "bg-gray-900 hover:opacity-90" : "bg-gray-300"}`}>{busy ? "Saving…" : "Add Teacher"}</button>
			</div>
		</form>
	);
};

export default function TeacherManagement() {
	const [teachers, setTeachers] = useState([]);
	const [loading, setLoading] = useState(true);
	const [busy, setBusy] = useState(false);
	const [error, setError] = useState("");

	useEffect(() => {
		DataAPI.list("teachers").then(setTeachers).finally(() => setLoading(false));
	}, []);

	return (
		<div className="space-y-6">
			<div>
				<h2 className="text-xl font-semibold">Teacher Data Management</h2>
				<p className="text-sm text-gray-500">Manage teachers and add new ones</p>
			</div>
			<Table
				teachers={teachers}
				onEdit={(t) => alert(`Edit ${t.teacher_name}`)}
				onDelete={async (id) => {
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
				}}
				loading={loading}
			/>
			<EntityForm onAdd={async (payload) => {
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
			}} busy={busy} error={error} />
		</div>
	);
}
