import { api } from './client';

export const providersApi = {
  register: (data) => api.post('/providers/register', data),
  list: (onlineOnly = false) => api.get(`/providers?online_only=${onlineOnly}`),
  get: (id) => api.get(`/providers/${id}`),
  setAvailability: (id, isSharing) => api.patch(`/providers/${id}/availability`, { is_sharing: isSharing }),
  updateResources: (id, data) => api.patch(`/providers/${id}/resources`, data),
  getJobs: (id) => api.get(`/providers/${id}/jobs`),
};
