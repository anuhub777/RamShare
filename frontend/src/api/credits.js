import { api } from './client';

export const creditsApi = {
  getBalance: () => api.get('/credits/balance'),
  getTransactions: (limit = 50, offset = 0) => api.get(`/credits/transactions?limit=${limit}&offset=${offset}`),
  estimate: (data) => api.post('/credits/estimate', data),
};
