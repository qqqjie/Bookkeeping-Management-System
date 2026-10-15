import request from './request'

export const categoriesApi = {
  list: () => request.get('/categories'),
  get: (id) => request.get(`/categories/${id}`),
  create: (data) => request.post('/categories', data),
  update: (id, data) => request.put(`/categories/${id}`, data),
  remove: (id) => request.delete(`/categories/${id}`)
}
