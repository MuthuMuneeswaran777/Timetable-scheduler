import { useEffect, useMemo, useState } from "react";
import { DataAPI } from "../services/api";

const CONFIG = {
	batches: {
		label: "Batches",
		columns: [
			{ key: "batch_id", label: "ID" },
			{ key: "batch_name", label: "Name" },
			{ key: "department", label: "Department" },
			{ key: "sem", label: "Sem" },
			{ key: "academic_year", label: "Year" },
		],
		defaults: { batch_name: "", department: "", sem: "", academic_year: "" },
	},
	subjects: {
		label: "Subjects",
		columns: [
			{ key: "subject_id", label: "ID" },
			{ key: "subject_name", label: "Name" },
			{ key: "teacher_id", label: "Teacher" },
			{ key: "sessions_per_week", label: "Per Week" },
			{ key: "is_lab", label: "Lab" },
		],
		defaults: { subject_name: "", teacher_id: "", sessions_per_week: 3, is_lab: false },
	},
	subject_offerings: {
		label: "Subject Offerings",
		columns: [
			{ key: "offering_id", label: "ID" },
			{ key: "subject_id", label: "Subject" },
			{ key: "teacher_id", label: "Teacher" },
			{ key: "batch_id", label: "Batch" },
			{ key: "sessions_per_week", label: "Per Week" },
		],
		defaults: { subject_id: "", teacher_id: "", batch_id: "", sessions_per_week: 3 },
	},
	rooms: {
		label: "Rooms",
		columns: [
			{ key: "room_id", label: "ID" },
			{ key: "room_name", label: "Name" },
			{ key: "capacity", label: "Capacity" },
			{ key: "room_type", label: "Type" },
		],
		defaults: { room_name: "", capacity: 30, room_type: "CLASSROOM" },
	},
};

export default function DataManager({ entity = "batches" }) {
	const cfg = CONFIG[entity];
	const [items, setItems] = useState([]);
	const [loading, setLoading] = useState(true);
	const [busy, setBusy] = useState(false);
	const [error, setError] = useState("");
	const [form, setForm] = useState(cfg.defaults);
	const [editingId, setEditingId] = useState(null);
	const [teachers, setTeachers] = useState([]);
	const [subjects, setSubjects] = useState([]);
	const [batches, setBatches] = useState([]);

	useEffect(() => {
		setLoading(true);
		Promise.all([
			DataAPI.list(entity),
			entity === "subjects" ? DataAPI.list("teachers") : Promise.resolve([]),
			entity === "subject_offerings" ? Promise.all([DataAPI.list("teachers"), DataAPI.list("subjects"), DataAPI.list("batches")]) : Promise.resolve([[], [], []]),
		])
			.then(([itemsRes, teachersRes, extrasRes]) => {
				setItems(itemsRes);
				setTeachers(teachersRes);
				if (entity === "subject_offerings") {
					setTeachers(extrasRes[0]);
					setSubjects(extrasRes[1]);
					setBatches(extrasRes[2]);
				}
			})
			.finally(() => setLoading(false));
		setForm(cfg.defaults);
		setEditingId(null);
	}, [entity]);

	function idKey() {
		return cfg.columns[0].key;
	}

	function onChange(k, v) {
		let value = v;
		if (k === "sessions_per_week" || k === "capacity" || k.endsWith("_id")) {
			value = v === "" ? "" : Number(v);
		}
		if (k === "is_lab") {
			value = !!v;
		}
		setForm((f) => ({ ...f, [k]: value }));
	}

	function validate() {
		for (const [k, v] of Object.entries(form)) {
			if (typeof v === "string" && k.includes("name") && v.trim() === "") {
				return `${k} is required`;
			}
		}
		return "";
	}

	async function onSubmit(e) {
		e.preventDefault();
		const msg = validate();
		if (msg) {
			setError(msg);
			return;
		}
		setBusy(true);
		setError("");
		try {
			if (editingId) {
				const updated = await DataAPI.update(entity, editingId, form);
				setItems((prev) => prev.map((it) => (it[idKey()] === editingId ? updated : it)));
				setEditingId(null);
				setForm(cfg.defaults);
			} else {
				const created = await DataAPI.create(entity, form);
				setItems((prev) => [created, ...prev]);
				setForm(cfg.defaults);
			}
		} catch (e) {
			setError("Failed to save");
		} finally {
			setBusy(false);
		}
	}

	return (
		<div className="space-y-6">
			<div>
				<h2 className="text-xl font-semibold">{cfg.label} Management</h2>
				<p className="text-sm text-gray-500">Manage {cfg.label.toLowerCase()}</p>
			</div>
			<div className="overflow-x-auto rounded-lg border bg-white">
				<table className="min-w-full text-sm">
					<thead className="bg-gray-50 text-left">
						<tr>
							{cfg.columns.map((c) => (
								<th key={c.key} className="px-4 py-3 font-medium text-gray-600">{c.label}</th>
							))}
							<th className="px-4 py-3 font-medium text-gray-600">Actions</th>
						</tr>
					</thead>
					<tbody>
						{loading ? (
							<tr><td className="px-4 py-6 text-center" colSpan={cfg.columns.length + 1}>Loading…</td></tr>
						) : items.length === 0 ? (
							<tr><td className="px-4 py-6 text-center" colSpan={cfg.columns.length + 1}>No data</td></tr>
						) : items.map((it) => (
							<tr key={it[idKey()]} className="border-t">
								{cfg.columns.map((c) => (
									<td key={c.key} className="px-4 py-3">{String(it[c.key] ?? "")}</td>
								))}
								<td className="px-4 py-3">
									<div className="flex gap-2">
										<button className="rounded-md border px-3 py-1 hover:bg-gray-50" onClick={() => { setEditingId(it[idKey()]); const next = {}; for (const k of Object.keys(cfg.defaults)) next[k] = it[k] ?? cfg.defaults[k]; setForm(next); }}>Edit</button>
										<button className="rounded-md bg-red-600 px-3 py-1 text-white hover:opacity-90" onClick={async () => {
											setBusy(true);
											await DataAPI.remove(entity, it[idKey()]);
											setItems((prev) => prev.filter((x) => x[idKey()] !== it[idKey()]));
											setBusy(false);
										}}>Delete</button>
									</div>
								</td>
							</tr>
						))}
					</tbody>
				</table>
			</div>

			<form onSubmit={onSubmit} className="space-y-3 rounded-lg border bg-white p-4">
				{Object.entries(cfg.defaults).map(([k, v]) => (
					<div key={k}>
						<label className="block text-sm font-medium">{k}</label>
						{entity === "subjects" && k === "teacher_id" ? (
							<select className="mt-1 w-full rounded-md border px-3 py-2" value={String(form[k] ?? "")} onChange={(e) => onChange(k, e.target.value === "" ? "" : Number(e.target.value))}>
								<option value="">Select teacher</option>
								{teachers.map((t) => (
									<option key={t.teacher_id} value={t.teacher_id}>{t.teacher_name}</option>
								))}
							</select>
						) : entity === "subject_offerings" && k === "teacher_id" ? (
							<select className="mt-1 w-full rounded-md border px-3 py-2" value={String(form[k] ?? "")} onChange={(e) => onChange(k, e.target.value === "" ? "" : Number(e.target.value))}>
								<option value="">Select teacher</option>
								{teachers.map((t) => (
									<option key={t.teacher_id} value={t.teacher_id}>{t.teacher_name}</option>
								))}
							</select>
						) : entity === "subject_offerings" && k === "subject_id" ? (
							<select className="mt-1 w-full rounded-md border px-3 py-2" value={String(form[k] ?? "")} onChange={(e) => onChange(k, e.target.value === "" ? "" : Number(e.target.value))}>
								<option value="">Select subject</option>
								{subjects.map((s) => (
									<option key={s.subject_id} value={s.subject_id}>{s.subject_name}</option>
								))}
							</select>
						) : entity === "subject_offerings" && k === "batch_id" ? (
							<select className="mt-1 w-full rounded-md border px-3 py-2" value={String(form[k] ?? "")} onChange={(e) => onChange(k, e.target.value === "" ? "" : Number(e.target.value))}>
								<option value="">Select batch</option>
								{batches.map((b) => (
									<option key={b.batch_id} value={b.batch_id}>{b.batch_name}</option>
								))}
							</select>
						) : typeof v === "boolean" ? (
							<label className="inline-flex items-center gap-2 mt-1">
								<input type="checkbox" checked={!!form[k]} onChange={(e) => onChange(k, e.target.checked)} />
								<span className="text-sm">Is lab</span>
							</label>
						) : typeof v === "number" ? (
							<input type="number" className="mt-1 w-full rounded-md border px-3 py-2" value={String(form[k] ?? "")} onChange={(e) => onChange(k, e.target.value)} />
						) : (
							<input className="mt-1 w-full rounded-md border px-3 py-2" value={String(form[k] ?? "")} onChange={(e) => onChange(k, e.target.value)} />
						)}
					</div>
				))}
				{error && <p className="text-xs text-red-600">{error}</p>}
				<div className="flex gap-2">
					<button disabled={busy} className="rounded-md bg-gray-900 px-4 py-2 text-white text-sm">{busy ? "Saving…" : editingId ? "Update" : "Add"}</button>
					{editingId && <button type="button" className="rounded-md border px-4 py-2 text-sm" onClick={() => { setEditingId(null); setForm(cfg.defaults); }}>Cancel</button>}
				</div>
			</form>
		</div>
	);
}
