import axios from "axios";

const api = axios.create({
	baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
});

export const DataAPI = {
	list: (entity) => api.get(`/data/${entity}`).then((r) => r.data),
	create: (entity, body) => api.post(`/data/${entity}`, body).then((r) => r.data),
	update: (entity, id, body) => api.put(`/data/${entity}/${id}`, body).then((r) => r.data),
	remove: (entity, id) => api.delete(`/data/${entity}/${id}`).then((r) => r.data),
};

export const TimetableAPI = {
	list: () => api.get(`/timetables`).then((r) => r.data),
	get: (id) => api.get(`/timetables/${id}`).then((r) => r.data),
	generate: (params) => api.post(`/timetables/generate`, null, { params }).then((r) => r.data),
	updateEntry: (entryId, body) => api.patch(`/timetables/update/${entryId}`, body).then((r) => r.data),
};

export default api;
