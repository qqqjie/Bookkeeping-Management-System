import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { authStore } from '@/stores/auth'

const service = axios.create({
  baseURL: 'http://localhost:8080/api/v1',
  timeout: 15000
})

service.interceptors.request.use(
  (config) => {
    const token = authStore.getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

service.interceptors.response.use(
  (response) => {
    const body = response.data
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code !== 200) {
        ElMessage.error(body.message || '请求失败')
        if (body.code === 401) {
          authStore.clear()
          router.push('/login')
        }
        return Promise.reject(new Error(body.message || '请求失败'))
      }
      return body.data
    }
    return body
  },
  (error) => {
    const status = error.response?.status
    const body = error.response?.data
    if (status === 401 || body?.code === 401) {
      authStore.clear()
      ElMessage.error('登录已过期，请重新登录')
      router.push('/login')
    } else {
      ElMessage.error(body?.message || error.message || '网络错误')
    }
    return Promise.reject(error)
  }
)

export default service
