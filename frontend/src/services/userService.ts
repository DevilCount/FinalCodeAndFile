/**
 * 用户管理服务
 * 封装用户相关的业务逻辑和API调用
 */

import { userApi } from '@/api/user'
import type { User, LoginParams, PageParams } from '@/types'

class UserService {
  /**
   * 用户登录
   */
  async login(username: string, password: string) {
    try {
      const response = await userApi.login({ username, password } as LoginParams)
      return response.data
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    }
  }

  /**
   * 用户注册
   */
  async register(userData: User) {
    try {
      const response = await userApi.register(userData)
      return response.data
    } catch (error) {
      console.error('注册失败:', error)
      throw error
    }
  }

  /**
   * 根据ID获取用户信息
   */
  async getUserById(id: number) {
    try {
      const response = await userApi.getUserById(id)
      return response.data
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    }
  }

  /**
   * 获取用户列表（分页）
   */
  async getUserList(params?: PageParams) {
    const response = await userApi.listUsers(params)
    return response.data || { records: [], total: 0, page: 1, pageSize: 10 }
  }

  /**
   * 根据角色获取用户列表
   */
  async getUsersByRole(role: string) {
    const response = await userApi.getUsersByRole(role)
    return response.data || []
  }

  /**
   * 更新用户信息
   */
  async updateUser(id: number, data: Partial<User>) {
    try {
      const response = await userApi.updateUser(id, data)
      return response.data
    } catch (error) {
      console.error('更新用户信息失败:', error)
      throw error
    }
  }

  /**
   * 删除用户
   */
  async deleteUser(id: number) {
    try {
      await userApi.deleteUser(id)
      return true
    } catch (error) {
      console.error('删除用户失败:', error)
      throw error
    }
  }

  /**
   * 搜索用户
   */
  async searchUsers(keyword: string, params?: PageParams) {
    const response = await userApi.listUsers({
      page: params?.page || 1,
      pageSize: params?.pageSize || 10,
      keyword
    })
    return response.data || { records: [], total: 0, page: 1, pageSize: 10 }
  }

  /**
   * 获取当前登录用户信息（从localStorage）
   */
  getCurrentUser(): User | null {
    try {
      const userStr = localStorage.getItem('user')
      return userStr ? JSON.parse(userStr) : null
    } catch (error) {
      console.error('获取当前用户信息失败:', error)
      return null
    }
  }

  /**
   * 检查是否已登录
   */
  isLoggedIn(): boolean {
    return !!localStorage.getItem('token')
  }

  /**
   * 获取当前用户角色
   */
  getCurrentUserRole(): string {
    const user = this.getCurrentUser()
    return user?.role || ''
  }

  /**
   * 检查是否为管理员
   */
  isAdmin(): boolean {
    return this.getCurrentUserRole() === 'ADMIN'
  }
}

// 导出单例实例
const userService = new UserService()
export default userService
