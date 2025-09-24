import axios from "axios";

const api = axios.create({
	baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

export const DataAPI = {
	list: (entity) => api.get(`/data/${entity}`).then((r) => r.data).catch(err => {
		console.error(`Failed to list ${entity}:`, err.response?.data || err.message);
		throw err;
	}),
	create: (entity, body) => api.post(`/data/${entity}`, body).then((r) => r.data).catch(err => {
		console.error(`Failed to create ${entity}:`, err.response?.data || err.message);
		throw err;
	}),
	update: (entity, id, body) => api.put(`/data/${entity}/${id}`, body).then((r) => r.data).catch(err => {
		console.error(`Failed to update ${entity} ${id}:`, err.response?.data || err.message);
		throw err;
	}),
	remove: (entity, id) => api.delete(`/data/${entity}/${id}`).then((r) => r.data).catch(err => {
		console.error(`Failed to delete ${entity} ${id}:`, err.response?.data || err.message);
		throw err;
	}),
};

export const TimetableAPI = {
	list: () => api.get(`/timetables`).then((r) => r.data),
	get: (id) => api.get(`/timetables/${id}`).then((r) => r.data),
	generate: (params) => api.post(`/timetables/generate`, null, { params }).then((r) => r.data),
	regenerate: (batchId) => api.post(`/timetables/regenerate/${batchId}`).then((r) => r.data),
	delete: (timetableId) => api.delete(`/timetables/${timetableId}`).then((r) => r.data),
	updateEntry: (entryId, body) => api.patch(`/timetables/update/${entryId}`, body).then((r) => r.data),
};

export default api;
