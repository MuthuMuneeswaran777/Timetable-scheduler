import { Fragment, useEffect, useState } from "react";
import { TimetableAPI, DataAPI } from "../services/api";

const StatCard = ({ label, value }) => (
	<div className="rounded-lg border bg-white p-4 shadow-sm flex items-center gap-4">
		<div className="h-10 w-10 rounded-md bg-gray-900 text-white grid place-items-center text-sm font-semibold">{label[0]}</div>
		<div>
			<p className="text-xs text-gray-500">{label}</p>
			<p className="text-2xl font-semibold mt-1">{value}</p>
		</div>
	</div>
);

const QuickActionButtons = ({ onCreate, onManage }) => (
	<div className="flex flex-wrap gap-3">
		<button className="inline-flex items-center gap-2 rounded-md bg-gray-900 px-4 py-2 text-white text-sm hover:opacity-90" onClick={onCreate}>
			<span>＋</span>
			<span>Create Timetable</span>
		</button>
		<button className="inline-flex items-center gap-2 rounded-md border px-4 py-2 text-sm hover:bg-gray-50" onClick={onManage}>
			<span>⚙</span>
			<span>Manage Data</span>
		</button>
	</div>
);

export default function AdminDashboard() {
	const [stats, setStats] = useState({ timetables: 0, pending: 0, recent: 0 });

	useEffect(() => {
		(async () => {
			try {
				const [timetables] = await Promise.all([
					TimetableAPI.list(),
				]);
				setStats({ timetables: timetables.length, pending: 0, recent: Math.min(12, timetables.length) });
			} catch (e) {
				// keep defaults
			}
		})();
	}, []);

	return (
		<Fragment>
			<div className="mb-6">
				<h2 className="text-xl font-semibold">Admin Dashboard</h2>
				<p className="text-sm text-gray-500">Overview and quick actions</p>
			</div>

			<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
				<StatCard label="Total Timetables" value={stats.timetables} />
				<StatCard label="Pending Approvals" value={stats.pending} />
				<StatCard label="Recent Changes" value={stats.recent} />
			</div>

			<QuickActionButtons onCreate={() => window.location.assign("/builder")} onManage={() => window.location.assign("/teachers")} />
		</Fragment>
	);
}
