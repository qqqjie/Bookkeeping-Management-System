import request from './request'

export const authApi = {
  register: (data) => request.post('/auth/register', data),
  login: (data) => request.post('/auth/login', data),
  me: () => request.get('/users/me'),
  updateMe: (data) => request.put('/users/me', data)
}
