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
	teachers: {
		label: "Teachers",
		columns: [
			{ key: "teacher_id", label: "ID" },
			{ key: "teacher_name", label: "Name" },
			{ key: "email", label: "Email" },
			{ key: "max_sessions_per_day", label: "Max Sessions/Day" },
			{ key: "max_sessions_per_week", label: "Max Sessions/Week" },
		],
		defaults: { teacher_name: "", email: "", max_sessions_per_day: 3, max_sessions_per_week: 15 },
	},
	subjects: {
		label: "Subjects",
		columns: [
			{ key: "subject_id", label: "ID" },
			{ key: "subject_name", label: "Name" },
			{ key: "teacher_name", label: "Teacher", isRelated: true },
			{ key: "sessions_per_week", label: "Per Week" },
			{ key: "is_lab", label: "Lab" },
		],
		defaults: { subject_name: "", teacher_id: "", sessions_per_week: 3, is_lab: false },
		needsRelatedData: true,
	},
	subject_offerings: {
		label: "Subject Offerings",
		columns: [
			{ key: "offering_id", label: "ID" },
			{ key: "subject_name", label: "Subject", isRelated: true },
			{ key: "teacher_name", label: "Teacher", isRelated: true },
			{ key: "batch_name", label: "Batch", isRelated: true },
			{ key: "sessions_per_week", label: "Per Week" },
			{ key: "max_sessions_per_day", label: "Max Per Day" },
		],
		defaults: { subject_id: "", teacher_id: "", batch_id: "", sessions_per_week: 3, max_sessions_per_day: 2 },
		needsRelatedData: true,
	},
	rooms: {
		label: "Rooms",
		columns: [
			{ key: "room_id", label: "ID" },
			{ key: "room_name", label: "Name" },
			{ key: "capacity", label: "Capacity" },
			{ key: "room_type", label: "Type" },
			{ key: "assigned_batch_name", label: "Assigned Batch", isRelated: true },
		],
		defaults: { room_name: "", capacity: 30, room_type: "CLASSROOM", assigned_batch_id: null },
		needsRelatedData: true,
	},
};

const enhanceWithRelatedData = (items, relatedData, entity) => {
	return items.map(item => {
		const enhanced = { ...item };
		
		// Add teacher names
		if (item.teacher_id && relatedData.teachers) {
			const teacher = relatedData.teachers.find(t => t.teacher_id === item.teacher_id);
			enhanced.teacher_name = teacher ? teacher.teacher_name : `Teacher ${item.teacher_id}`;
		}
		
		// Add subject names
		if (item.subject_id && relatedData.subjects) {
			const subject = relatedData.subjects.find(s => s.subject_id === item.subject_id);
			enhanced.subject_name = subject ? subject.subject_name : `Subject ${item.subject_id}`;
		}
		
		// Add batch names
		if (item.batch_id && relatedData.batches) {
			const batch = relatedData.batches.find(b => b.batch_id === item.batch_id);
			enhanced.batch_name = batch ? batch.batch_name : `Batch ${item.batch_id}`;
		}
		
		// Add assigned batch names for rooms
		if (item.assigned_batch_id && relatedData.batches) {
			const batch = relatedData.batches.find(b => b.batch_id === item.assigned_batch_id);
			enhanced.assigned_batch_name = batch ? batch.batch_name : `Batch ${item.assigned_batch_id}`;
		} else if (entity === "rooms") {
			enhanced.assigned_batch_name = "Unassigned";
		}
		
		return enhanced;
	});
};

export default function EnhancedDataManager({ entity = "batches" }) {
	const cfg = CONFIG[entity];
	const [items, setItems] = useState([]);
	const [loading, setLoading] = useState(true);
	const [busy, setBusy] = useState(false);
	const [error, setError] = useState("");
	const [form, setForm] = useState(cfg.defaults);
	const [editing, setEditing] = useState(null);
	const [relatedData, setRelatedData] = useState({
		teachers: [],
		subjects: [],
		batches: [],
	});

	useEffect(() => {
		const loadData = async () => {
			try {
				setLoading(true);
				
				// Load related data first if needed
				let related = { teachers: [], subjects: [], batches: [] };
				if (cfg.needsRelatedData) {
					const [teachers, subjects, batches] = await Promise.all([
						DataAPI.list("teachers"),
						DataAPI.list("subjects"),
						DataAPI.list("batches"),
					]);
					related = { teachers, subjects, batches };
					setRelatedData(related);
				}
				
				// Load main entity data
				const mainData = await DataAPI.list(entity);
				
				// Enhance with related data
				const enhancedData = enhanceWithRelatedData(mainData, related, entity);
				setItems(enhancedData);
				
			} catch (err) {
				setError("Failed to load data");
				console.error("Data loading error:", err);
			} finally {
				setLoading(false);
			}
		};
		
		loadData();
		setForm(cfg.defaults);
		setEditing(null);
	}, [entity]);

	const idKey = cfg.columns[0].key;

	const onChange = (key, value) => {
		let processedValue = value;
		if (key === "sessions_per_week" || key === "capacity" || key === "max_sessions_per_day") {
			processedValue = value === "" ? "" : Number(value);
		}
		if (key.endsWith("_id") && key !== "assigned_batch_id") {
			processedValue = value === "" ? "" : Number(value);
		}
		if (key === "assigned_batch_id") {
			// Handle assigned_batch_id specially - can be null
			processedValue = value === "" || value === null ? null : Number(value);
		}
		if (key === "is_lab") {
			processedValue = !!value;
		}
		setForm(prev => ({ ...prev, [key]: processedValue }));
	};

	const handleSubmit = async (e) => {
		e.preventDefault();
		setBusy(true);
		setError("");
		
		try {
			// Filter out enhanced fields that don't exist in the database
			const dbFields = { ...form };
			
			// Remove enhanced display fields
			delete dbFields.teacher_name;
			delete dbFields.subject_name;
			delete dbFields.batch_name;
			delete dbFields.assigned_batch_name;
			
			// Handle null values for foreign keys
			if (dbFields.assigned_batch_id === "") {
				dbFields.assigned_batch_id = null;
			}
			
			console.log("Submitting data:", dbFields);
			
			if (editing) {
				const updated = await DataAPI.update(entity, editing[idKey], dbFields);
				const enhanced = enhanceWithRelatedData([updated], relatedData, entity)[0];
				setItems(prev => prev.map(item => item[idKey] === editing[idKey] ? enhanced : item));
				setEditing(null);
			} else {
				const created = await DataAPI.create(entity, dbFields);
				const enhanced = enhanceWithRelatedData([created], relatedData, entity)[0];
				setItems(prev => [enhanced, ...prev]);
			}
			setForm(cfg.defaults);
		} catch (err) {
			const errorMessage = err.response?.data?.detail || err.message || err.toString();
			setError(`Failed to save item: ${errorMessage}`);
			console.error("Save error:", err);
			console.error("Error response:", err.response?.data);
		} finally {
			setBusy(false);
		}
	};

	const handleEdit = (item) => {
		setEditing(item);
		setForm({ ...cfg.defaults, ...item });
		setError("");
	};

	const handleDelete = async (id) => {
		if (!confirm("Are you sure you want to delete this item?")) return;
		
		setBusy(true);
		setError("");
		
		try {
			await DataAPI.remove(entity, id);
			setItems(prev => prev.filter(item => item[idKey] !== id));
		} catch (err) {
			setError("Failed to delete item");
			console.error("Delete error:", err);
		} finally {
			setBusy(false);
		}
	};

	const handleCancel = () => {
		setEditing(null);
		setForm(cfg.defaults);
		setError("");
	};

	const renderFormField = (column, index) => {
		const { key, label } = column;
		const value = form[key] || "";

		if (key === "is_lab") {
			return (
				<div key={key}>
					<label className="flex items-center space-x-2">
						<input
							type="checkbox"
							checked={!!value}
							onChange={(e) => onChange(key, e.target.checked)}
							className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
						/>
						<span className="text-sm font-medium text-gray-700">{label}</span>
					</label>
				</div>
			);
		}

		if (key === "room_type") {
			return (
				<div key={key}>
					<label className="block text-sm font-medium text-gray-700">{label}</label>
					<select
						value={value}
						onChange={(e) => onChange(key, e.target.value)}
						className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:ring-indigo-500"
					>
						<option value="CLASSROOM">Classroom</option>
						<option value="LAB">Lab</option>
						<option value="AUDITORIUM">Auditorium</option>
					</select>
				</div>
			);
		}

		if (key === "teacher_id" && relatedData.teachers.length > 0) {
			return (
				<div key={key}>
					<label className="block text-sm font-medium text-gray-700">{label}</label>
					<select
						value={value}
						onChange={(e) => onChange(key, e.target.value)}
						className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:ring-indigo-500"
					>
						<option value="">Select Teacher</option>
						{relatedData.teachers.map(teacher => (
							<option key={teacher.teacher_id} value={teacher.teacher_id}>
								{teacher.teacher_name}
							</option>
						))}
					</select>
				</div>
			);
		}

		if (key === "subject_id" && relatedData.subjects.length > 0) {
			return (
				<div key={key}>
					<label className="block text-sm font-medium text-gray-700">{label}</label>
					<select
						value={value}
						onChange={(e) => onChange(key, e.target.value)}
						className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:ring-indigo-500"
					>
						<option value="">Select Subject</option>
						{relatedData.subjects.map(subject => (
							<option key={subject.subject_id} value={subject.subject_id}>
								{subject.subject_name}
							</option>
						))}
					</select>
				</div>
			);
		}

		if (key === "batch_id" && relatedData.batches.length > 0) {
			return (
				<div key={key}>
					<label className="block text-sm font-medium text-gray-700">{label}</label>
					<select
						value={value}
						onChange={(e) => onChange(key, e.target.value)}
						className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:ring-indigo-500"
					>
						<option value="">Select Batch</option>
						{relatedData.batches.map(batch => (
							<option key={batch.batch_id} value={batch.batch_id}>
								{batch.batch_name}
							</option>
						))}
					</select>
				</div>
			);
		}

		if (key === "assigned_batch_id" && relatedData.batches && relatedData.batches.length > 0) {
			return (
				<div key={key}>
					<label className="block text-sm font-medium text-gray-700">Assign to Batch</label>
					<select
						value={value || ""}
						onChange={(e) => onChange(key, e.target.value || null)}
						className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:ring-indigo-500"
					>
						<option value="">Unassigned</option>
						{relatedData.batches.map(batch => (
							<option key={batch.batch_id} value={batch.batch_id}>
								{batch.batch_name}
							</option>
						))}
					</select>
				</div>
			);
		}

		if (key === "subject_id" && relatedData.subjects && relatedData.subjects.length > 0) {
			return (
				<div key={key}>
					<label className="block text-sm font-medium text-gray-700">Subject</label>
					<select
						value={value || ""}
						onChange={(e) => onChange(key, e.target.value)}
						className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:ring-indigo-500"
						required
					>
						<option value="">Select Subject</option>
						{relatedData.subjects.map(subject => (
							<option key={subject.subject_id} value={subject.subject_id}>
								{subject.subject_name}
							</option>
						))}
					</select>
				</div>
			);
		}

		if (key === "teacher_id" && relatedData.teachers && relatedData.teachers.length > 0) {
			return (
				<div key={key}>
					<label className="block text-sm font-medium text-gray-700">Teacher</label>
					<select
						value={value || ""}
						onChange={(e) => onChange(key, e.target.value)}
						className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:ring-indigo-500"
						required
					>
						<option value="">Select Teacher</option>
						{relatedData.teachers.map(teacher => (
							<option key={teacher.teacher_id} value={teacher.teacher_id}>
								{teacher.teacher_name}
							</option>
						))}
					</select>
				</div>
			);
		}

		if (key === "batch_id" && relatedData.batches && relatedData.batches.length > 0) {
			return (
				<div key={key}>
					<label className="block text-sm font-medium text-gray-700">Batch</label>
					<select
						value={value || ""}
						onChange={(e) => onChange(key, e.target.value)}
						className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:ring-indigo-500"
						required
					>
						<option value="">Select Batch</option>
						{relatedData.batches.map(batch => (
							<option key={batch.batch_id} value={batch.batch_id}>
								{batch.batch_name}
							</option>
						))}
					</select>
				</div>
			);
		}

		// Skip ID fields and related fields in form (except those with special dropdown handling)
		const specialIdFields = ["assigned_batch_id", "subject_id", "teacher_id", "batch_id"];
		if ((key.endsWith("_id") && !specialIdFields.includes(key)) || column.isRelated) {
			return null;
		}

		const inputType = key === "capacity" || key === "sessions_per_week" || key === "max_sessions_per_day" ? "number" : "text";

		return (
			<div key={key}>
				<label className="block text-sm font-medium text-gray-700">{label}</label>
				<input
					type={inputType}
					value={value}
					onChange={(e) => onChange(key, e.target.value)}
					className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:ring-indigo-500"
					placeholder={`Enter ${label.toLowerCase()}`}
					min={inputType === "number" ? "1" : undefined}
				/>
			</div>
		);
	};

	const renderCellValue = (item, column) => {
		const value = item[column.key];
		
		if (column.key === "is_lab") {
			return value ? "✅ Yes" : "❌ No";
		}
		
		if (column.key === "room_type") {
			const typeEmoji = {
				"LAB": "🔬",
				"CLASSROOM": "📚",
				"AUDITORIUM": "🎭"
			};
			return `${typeEmoji[value] || "📍"} ${value || "N/A"}`;
		}
		
		if (column.key === "assigned_batch_name") {
			return value === "Unassigned" ? "🔓 Unassigned" : `🎯 ${value}`;
		}
		
		return value || "—";
	};

	return (
		<div className="space-y-6">
			<div>
				<h2 className="text-2xl font-bold text-gray-900">{cfg.label} Management</h2>
				<p className="text-gray-600">Manage {cfg.label.toLowerCase()} with enhanced display names</p>
			</div>

			{/* Form */}
			<form onSubmit={handleSubmit} className="space-y-4 rounded-lg border bg-white p-6">
				<div className="flex items-center justify-between">
					<h3 className="text-lg font-medium text-gray-900">
						{editing ? `Edit ${cfg.label.slice(0, -1)}` : `Add New ${cfg.label.slice(0, -1)}`}
					</h3>
					{editing && (
						<button
							type="button"
							onClick={handleCancel}
							className="text-gray-400 hover:text-gray-600"
						>
							<svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
							</svg>
						</button>
					)}
				</div>

				<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
					{cfg.columns.map((column, index) => renderFormField(column, index)).filter(Boolean)}
				</div>

				{error && <p className="text-sm text-red-600 bg-red-50 p-3 rounded-md">{error}</p>}

				<div className="flex gap-3 pt-2">
					<button
						type="submit"
						disabled={busy}
						className={`px-6 py-2 rounded-md text-white font-medium transition-colors ${
							busy ? "bg-gray-300 cursor-not-allowed" : "bg-indigo-600 hover:bg-indigo-700"
						}`}
					>
						{busy ? "Saving..." : (editing ? `Update ${cfg.label.slice(0, -1)}` : `Add ${cfg.label.slice(0, -1)}`)}
					</button>

					{editing && (
						<button
							type="button"
							onClick={handleCancel}
							className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
						>
							Cancel
						</button>
					)}
				</div>
			</form>

			{/* Table */}
			<div className="rounded-lg border bg-white overflow-hidden">
				<div className="px-6 py-4 border-b border-gray-200">
					<h3 className="text-lg font-medium text-gray-900">All {cfg.label}</h3>
				</div>
				
				<div className="overflow-x-auto">
					<table className="min-w-full divide-y divide-gray-200">
						<thead className="bg-gray-50">
							<tr>
								{cfg.columns.map(column => (
									<th key={column.key} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
										{column.label}
									</th>
								))}
								<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
									Actions
								</th>
							</tr>
						</thead>
						<tbody className="bg-white divide-y divide-gray-200">
							{loading ? (
								<tr>
									<td colSpan={cfg.columns.length + 1} className="px-6 py-12 text-center text-gray-500">
										Loading...
									</td>
								</tr>
							) : items.length === 0 ? (
								<tr>
									<td colSpan={cfg.columns.length + 1} className="px-6 py-12 text-center text-gray-500">
										No {cfg.label.toLowerCase()} found
									</td>
								</tr>
							) : (
								items.map(item => (
									<tr key={item[idKey]} className="hover:bg-gray-50">
										{cfg.columns.map(column => (
											<td key={column.key} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
												{renderCellValue(item, column)}
											</td>
										))}
										<td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
											<div className="flex space-x-2">
												<button
													onClick={() => handleEdit(item)}
													className="text-indigo-600 hover:text-indigo-900 transition-colors"
												>
													Edit
												</button>
												<button
													onClick={() => handleDelete(item[idKey])}
													className="text-red-600 hover:text-red-900 transition-colors"
												>
													Delete
												</button>
											</div>
										</td>
									</tr>
								))
							)}
						</tbody>
					</table>
				</div>
			</div>
		</div>
	);
}
