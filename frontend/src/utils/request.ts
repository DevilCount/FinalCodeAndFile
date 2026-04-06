import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores'
import type { ApiResponse } from '@/types'

// 401错误处理锁，防止并发请求时多次logout/跳转
let isLoggingOut = false

// 统一的401未授权处理函数
const handleUnauthorized = () => {
  // 如果已经在处理中，直接返回，避免重复执行
  if (isLoggingOut) return

  // 设置锁
  isLoggingOut = true

  // 执行登出操作
  const userStore = useUserStore()
  userStore.logout()

  // 跳转到登录页（避免在登录页重复跳转）
  if (window.location.pathname !== '/login') {
    window.location.href = '/login'
  }

  // 5秒后重置锁，允许下次处理
  setTimeout(() => {
    isLoggingOut = false
  }, 5000)
}

// API超时配置（毫秒）
const TIMEOUT_CONFIG = {
  default: parseInt(import.meta.env.VITE_API_TIMEOUT || '15000'),
  upload: parseInt(import.meta.env.VITE_API_UPLOAD_TIMEOUT || '60000'),
  download: parseInt(import.meta.env.VITE_API_DOWNLOAD_TIMEOUT || '30000')
} as const

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: TIMEOUT_CONFIG.default,
  headers: {
    'Content-Type': 'application/json;charset=utf-8'
  }
})

// 请求拦截器
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const userStore = useUserStore()
    if (userStore.token && config.headers) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error: any) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const res = response.data

    // 如果返回的状态码不是200，说明接口有问题
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')

      // 401: 未登录或token过期 - 自动跳转到登录页
      if (res.code === 401) {
        handleUnauthorized()
      }

      // 403: 无权限访问
      if (res.code === 403) {
        ElMessage.warning('您没有权限执行此操作')
      }

      return Promise.reject(new Error(res.message || '请求失败'))
    }

    return res as any
  },
  (error: any) => {
    console.error('API请求错误:', error)

    let message = '网络错误，请稍后重试'

    if (error.response) {
      // 服务器返回了响应，但状态码不在2xx范围内
      switch (error.response.status) {
        case 400:
          message = error.response.data?.message || '请求参数错误'
          break
        case 401:
          message = '未授权或登录已过期，请重新登录'
          // 使用统一的401处理函数
          handleUnauthorized()
          break
        case 403:
          message = '拒绝访问，您没有权限执行此操作'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 405:
          message = '请求方法不允许'
          break
        case 408:
          message = '请求超时'
          break
        case 500:
          message = error.response.data?.message || '服务器内部错误'
          break
        case 502:
          message = '网关错误'
          break
        case 503:
          message = '服务不可用'
          break
        case 504:
          message = '网关超时'
          break
        default:
          message = `请求失败 (${error.response.status})`
      }
    } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      // 请求超时
      message = '请求超时，请检查网络连接后重试'
    } else if (error.message.includes('Network Error') || !navigator.onLine) {
      // 网络断开
      message = '网络连接失败，请检查网络设置'
    }

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// 请求方法封装
export default class Request {
  static get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.get(url, config) as Promise<ApiResponse<T>>
  }

  static post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.post(url, data, config) as Promise<ApiResponse<T>>
  }

  static put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.put(url, data, config) as Promise<ApiResponse<T>>
  }

  static delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return service.delete(url, config) as Promise<ApiResponse<T>>
  }
}
