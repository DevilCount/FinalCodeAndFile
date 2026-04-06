import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, UserRole } from '@/types'

// 安全解析localStorage中的用户数据
const getStoredUser = (): User | null => {
  try {
    const stored = localStorage.getItem('user')
    return stored ? JSON.parse(stored) : null
  } catch (e) {
    console.warn('Failed to parse stored user data:', e)
    return null
  }
}

export const useUserStore = defineStore(
  'user',
  () => {
    // State
    const token = ref<string>(localStorage.getItem('token') || '')
    const user = ref<User | null>(getStoredUser())

    // Getters
    const isLoggedIn = computed(() => !!token.value)
    const userName = computed(() => user.value?.realName || user.value?.username || '未知用户')
    const userRole = computed((): UserRole | '' => user.value?.role || '')
    const isAdmin = computed(() => user.value?.role === 'ADMIN')

    // Actions
    const setToken = (newToken: string) => {
      token.value = newToken
    }

    const setUser = (userData: User | null) => {
      user.value = userData
    }

    const logout = () => {
      token.value = ''
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }

    // 从后端获取用户信息
    const fetchUserInfo = async () => {
      // 如果已有用户信息，直接返回
      if (user.value) return user.value

      // TODO: 实际项目中这里应该调用API获取用户信息
      // const response = await userService.getCurrentUser()
      // setUser(response)
      return user.value
    }

    return {
      token,
      user,
      isLoggedIn,
      userName,
      userRole,
      isAdmin,
      setToken,
      setUser,
      logout,
      fetchUserInfo
    }
  },
  {
    persist: {
      key: 'user-store',
      storage: localStorage,
      paths: ['token', 'user']
    }
  }
)
