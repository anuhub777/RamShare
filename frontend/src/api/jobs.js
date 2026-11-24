import { api } from './client';

export const jobsApi = {
  submit: (data) => api.post('/jobs', data),
  list: (status = null) => api.get(status ? `/jobs?status=${status}` : '/jobs'),
  get: (id) => api.get(`/jobs/${id}`),
  cancel: (id) => api.post(`/jobs/${id}/cancel`),
  getResult: (id) => api.get(`/jobs/${id}/result`),
};
