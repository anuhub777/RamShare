import { api } from './client';

export const marketplaceApi = {
  getStatistics: () => api.get('/marketplace/statistics'),
  getResources: () => api.get('/marketplace/resources'),
};
