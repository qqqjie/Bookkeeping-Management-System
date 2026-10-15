import request from './request'

export const accountsApi = {
  list: () => request.get('/accounts'),
  get: (id) => request.get(`/accounts/${id}`),
  create: (data) => request.post('/accounts', data),
  update: (id, data) => request.put(`/accounts/${id}`, data),
  remove: (id) => request.delete(`/accounts/${id}`),
  balance: (id) => request.get(`/accounts/${id}/balance`)
}
