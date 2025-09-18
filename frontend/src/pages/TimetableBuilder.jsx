import { useEffect, useMemo, useState } from "react";
import { TimetableAPI, DataAPI } from "../services/api";

const days = ["Mon", "Tue", "Wed", "Thu", "Fri"];
const periods = [1, 2, 3, 4, 5, 6, 7, 8];

function colorForSubject(name) {
	const palette = [
		"bg-rose-100 text-rose-900 border-rose-200",
		"bg-sky-100 text-sky-900 border-sky-200",
		"bg-emerald-100 text-emerald-900 border-emerald-200",
		"bg-amber-100 text-amber-900 border-amber-200",
		"bg-violet-100 text-violet-900 border-violet-200",
		"bg-cyan-100 text-cyan-900 border-cyan-200",
		"bg-lime-100 text-lime-900 border-lime-200",
	];
	let hash = 0;
	for (let i = 0; i < name.length; i++) hash = (hash * 31 + name.charCodeAt(i)) >>> 0;
	return palette[hash % palette.length];
}

function TimetableCell({ cell, isDragging, isGhost }) {
	const color = colorForSubject(cell.subject_name || "");
	return (
		<div className={`rounded-md border p-2 text-xs h-20 relative ${color} ${isGhost ? "opacity-40 border-dashed" : ""}`}>
			<div className="font-medium truncate">{cell.subject_name ? `${cell.subject_name} (${cell.subject_id ?? ""})` : "—"}</div>
			<div className="text-gray-700 truncate">{cell.teacher_name || ""}</div>
			<div className="text-gray-600 truncate">{cell.room_name ? `Room ${cell.room_name}` : ""}</div>
			{isDragging && (
				<div className="absolute inset-0 rounded-md ring-2 ring-gray-900 pointer-events-none"></div>
			)}
		</div>
	);
}

function FilterPanel({ filters, setFilters, onExportIcs }) {
	return (
		<aside className="w-full lg:w-72 shrink-0 rounded-lg border bg-white p-4 h-max">
			<h3 className="text-sm font-semibold mb-3">Filters</h3>
			<div className="space-y-3 text-sm">
				<div>
					<label className="block text-gray-600">Batch</label>
					<input value={filters.batch} onChange={(e) => setFilters({ ...filters, batch: e.target.value })} className="mt-1 w-full rounded-md border px-3 py-2" placeholder="e.g., CSE-3A" />
				</div>
				<div>
					<label className="block text-gray-600">Teacher</label>
					<input value={filters.teacher} onChange={(e) => setFilters({ ...filters, teacher: e.target.value })} className="mt-1 w-full rounded-md border px-3 py-2" placeholder="e.g., Sharma" />
				</div>
				<div>
					<label className="block text-gray-600">Room</label>
					<input value={filters.room} onChange={(e) => setFilters({ ...filters, room: e.target.value })} className="mt-1 w-full rounded-md border px-3 py-2" placeholder="e.g., 101" />
				</div>
				<button onClick={onExportIcs} className="w-full rounded-md bg-gray-900 px-4 py-2 text-white text-sm">Export ICS</button>
			</div>
		</aside>
	);
}

function buildKey(day, period) {
	return `${day}-${period}`;
}

export default function TimetableBuilder() {
	const [filters, setFilters] = useState({ batch: "", teacher: "", room: "" });
	const [dragging, setDragging] = useState(null);
	const [ghost, setGhost] = useState(null);
	const [timetableId, setTimetableId] = useState(null);
	const [entries, setEntries] = useState([]);
	const [loading, setLoading] = useState(false);
	const [busy, setBusy] = useState(false);
	const [error, setError] = useState("");
	const [batches, setBatches] = useState([]);
	const [selectedBatchId, setSelectedBatchId] = useState(1);
	const [toast, setToast] = useState("");

	useEffect(() => {
		(async () => {
			setLoading(true);
			setError("");
			try {
				const [list, batchesList] = await Promise.all([
					TimetableAPI.list(),
					DataAPI.list("batches"),
				]);
				setBatches(batchesList);
				if (batchesList.length && !selectedBatchId) setSelectedBatchId(batchesList[0].batch_id);
				if (list.length) {
					const latest = list[list.length - 1];
					setTimetableId(latest.timetable_id);
					const data = await TimetableAPI.get(latest.timetable_id);
					setEntries(data.entries);
				}
			} catch (e) {
				setError("Failed to load timetables");
			} finally {
				setLoading(false);
			}
		})();
	}, []);

	const grid = useMemo(() => {
		const map = new Map(entries.map((e) => [buildKey(e.day_of_week, e.period_number), e]));
		return days.map((d) => periods.map((p) => map.get(buildKey(d, p)) || { day_of_week: d, period_number: p }));
	}, [entries]);

	async function handleGenerate() {
		setBusy(true);
		setError("");
		try {
			const tt = await TimetableAPI.generate({ batch_id: selectedBatchId || 1 });
			setTimetableId(tt.timetable_id);
			const data = await TimetableAPI.get(tt.timetable_id);
			setEntries(data.entries);
		} catch (e) {
			setError("Failed to generate timetable");
		} finally {
			setBusy(false);
		}
	}

	async function handleDrop(target) {
		if (!dragging || !dragging.entry_id) return;
		setBusy(true);
		try {
			const updated = await TimetableAPI.updateEntry(dragging.entry_id, {
				day_of_week: target.day_of_week,
				period_number: target.period_number,
			});
			setEntries((prev) => prev.map((e) => (e.entry_id === updated.entry_id ? { ...e, ...updated } : e)));
			setToast("Updated");
			setTimeout(() => setToast(""), 1500);
		} catch (e) {
			const msg = e?.response?.data?.detail || "Invalid move";
			setError(msg);
			setTimeout(() => setError(""), 2500);
		} finally {
			setBusy(false);
			setDragging(null);
			setGhost(null);
		}
	}

	function exportICS() {
		if (!timetableId) return;
		const lines = [
			"BEGIN:VCALENDAR",
			"VERSION:2.0",
			"PRODID:-//TimetableManager//EN",
		];
		for (const e of entries) {
			if (!e.subject_name) continue;
			lines.push("BEGIN:VEVENT");
			lines.push(`SUMMARY:${e.subject_name} (${e.subject_id}) - ${e.teacher_name || ""}`);
			lines.push(`LOCATION:${e.room_name || ""}`);
			lines.push(`DESCRIPTION:Day ${e.day_of_week} Period ${e.period_number}`);
			lines.push("END:VEVENT");
		}
		lines.push("END:VCALENDAR");
		const blob = new Blob([lines.join("\r\n")], { type: "text/calendar;charset=utf-8" });
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = `timetable-${timetableId}.ics`;
		a.click();
		URL.revokeObjectURL(url);
	}

	return (
		<div className="flex flex-col lg:flex-row gap-6">
			<div className="flex-1">
				<div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
					<div>
						<h2 className="text-xl font-semibold">Timetable Builder</h2>
						<p className="text-sm text-gray-500">Select a batch and generate. Drag cells to update.</p>
					</div>
					<div className="flex gap-2 items-center">
						<select className="rounded-md border px-3 py-2 text-sm" value={selectedBatchId} onChange={(e) => setSelectedBatchId(Number(e.target.value))}>
							{batches.length === 0 ? <option value={1}>Batch 1</option> : batches.map((b) => (
								<option key={b.batch_id} value={b.batch_id}>{b.batch_name || `Batch ${b.batch_id}`}</option>
							))}
						</select>
						<button onClick={handleGenerate} disabled={busy} className="rounded-md bg-gray-900 px-4 py-2 text-white text-sm disabled:opacity-50">{busy ? "Working…" : "Generate"}</button>
					</div>
				</div>
				{(error || toast) && <p className={`text-sm mb-2 ${error ? "text-red-600" : "text-emerald-700"}`}>{error || toast}</p>}
				<div className="overflow-x-auto rounded-lg border bg-white">
					<table className="min-w-full text-sm select-none">
						<thead>
							<tr className="bg-gray-50">
								<th className="px-3 py-2 text-left font-medium text-gray-600">Day \\ Period</th>
								{periods.map((p) => (
									<th key={p} className="px-3 py-2 text-left font-medium text-gray-600">{p}</th>
								))}
							</tr>
						</thead>
						<tbody>
							{grid.map((row, dIdx) => (
								<tr key={dIdx} className="align-top">
									<td className="px-3 py-2 font-medium bg-gray-50 sticky left-0">{days[dIdx]}</td>
									{row.map((cell) => {
										const isDragging = dragging && dragging.entry_id === cell.entry_id;
										const isGhost = ghost && ghost.day_of_week === cell.day_of_week && ghost.period_number === cell.period_number;
										return (
											<td key={`${cell.day_of_week}-${cell.period_number}`} className="p-2"
												onMouseEnter={() => setGhost(cell)}
												onMouseUp={() => ghost && handleDrop(cell)}
											>
												<div
													className="cursor-move"
													onMouseDown={() => cell.entry_id && setDragging(cell)}
												>
													<TimetableCell cell={cell} isDragging={isDragging} isGhost={isGhost} />
												</div>
											</td>
										);
									})}
								</tr>
							))}
						</tbody>
					</table>
				</div>
			</div>

			<FilterPanel filters={filters} setFilters={setFilters} onExportIcs={exportICS} />
		</div>
	);
}
