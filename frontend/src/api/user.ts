import Request from '@/utils/request'
import type { ApiResponse, User, LoginParams, LoginResponse, PageParams, PageResult } from '@/types'

export const userApi = {
  // 登录
  login: (data: LoginParams): Promise<ApiResponse<LoginResponse>> => {
    return Request.post('/user/login', data)
  },

  // 注册
  register: (data: User): Promise<ApiResponse<User>> => {
    return Request.post('/user/register', data)
  },

  // 根据ID获取用户
  getUserById: (id: number): Promise<ApiResponse<User>> => {
    return Request.get(`/user/${id}`)
  },

  // 根据角色获取用户列表
  getUsersByRole: (role: string): Promise<ApiResponse<User[]>> => {
    return Request.get(`/user/role/${role}`)
  },

  // 获取用户列表（分页）
  listUsers: (params?: PageParams): Promise<ApiResponse<PageResult<User>>> => {
    return Request.get('/user/list', { params })
  },

  // 更新用户
  updateUser: (id: number, data: Partial<User>): Promise<ApiResponse<User>> => {
    return Request.put(`/user/${id}`, data)
  },

  // 删除用户
  deleteUser: (id: number): Promise<ApiResponse<void>> => {
    return Request.delete(`/user/${id}`)
  }
}
