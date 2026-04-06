import Request from '@/utils/request'
import type { ApiResponse, DashboardStats } from '@/types'

export const dashboardApi = {
  // 获取仪表盘统计数据
  getStats: (): Promise<ApiResponse<DashboardStats>> => {
    return Request.get('/dashboard/stats')
  },

  // 获取标本状态分布
  getSampleStatusStats: (period: string = 'today'): Promise<ApiResponse<any[]>> => {
    return Request.get('/dashboard/sample-status', { params: { period } })
  },

  // 获取检验趋势数据
  getTestTrend: (days: number = 7): Promise<ApiResponse<any>> => {
    return Request.get('/dashboard/test-trend', { params: { days } })
  },

  // 获取待办事项
  getTodoList: (): Promise<ApiResponse<any[]>> => {
    return Request.get('/dashboard/todos')
  },

  // 获取热门检验项目
  getHotTestItems: (): Promise<ApiResponse<any[]>> => {
    return Request.get('/dashboard/hot-items')
  },

  // 获取最近操作日志
  getRecentLogs: (limit: number = 10): Promise<ApiResponse<any[]>> => {
    return Request.get('/dashboard/recent-logs', { params: { limit } })
  }
}
