import request from './request'

export const transactionsApi = {
  list: (params) => request.get('/transactions', { params }),
  get: (id) => request.get(`/transactions/${id}`),
  create: (data) => request.post('/transactions', data),
  update: (id, data) => request.put(`/transactions/${id}`, data),
  remove: (id) => request.delete(`/transactions/${id}`)
}
