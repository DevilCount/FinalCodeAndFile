/**
 * 标本管理服务
 * 封装标本相关的业务逻辑和API调用
 */

import { sampleApi } from '@/api/sample'
import type { Sample, PageParams, SampleStatus } from '@/types'

class SampleService {
  /**
   * 获取标本列表
   */
  async getSampleList(params?: PageParams) {
    try {
      const response = await sampleApi.listSamples(params)
      return response.data || { records: [], total: 0, page: 1, pageSize: 10 }
    } catch (error) {
      console.error('获取标本列表失败:', error)
      return { records: [], total: 0, page: 1, pageSize: 10 }
    }
  }

  /**
   * 创建标本
   */
  async createSample(data: Partial<Sample>) {
    try {
      const response = await sampleApi.createSample(data)
      return response.data
    } catch (error) {
      console.error('创建标本失败:', error)
      throw error
    }
  }

  /**
   * 根据ID获取标本详情
   */
  async getSampleById(id: number) {
    try {
      const response = await sampleApi.getSampleById(id)
      return response.data
    } catch (error) {
      console.error('获取标本详情失败:', error)
      throw error
    }
  }

  /**
   * 扫码查询标本
   */
  async scanSample(sampleNo: string) {
    try {
      const response = await sampleApi.scanSample(sampleNo)
      return response.data
    } catch (error) {
      console.error('扫码查询失败:', error)
      throw error
    }
  }

  /**
   * 更新标本状态
   */
  async updateSampleStatus(id: number, status: SampleStatus, operatorInfo?: { operatorId?: number; operatorName?: string }) {
    try {
      const response = await sampleApi.updateStatus(id, {
        status,
        ...operatorInfo
      })
      return response.data
    } catch (error) {
      console.error('更新标本状态失败:', error)
      throw error
    }
  }

  /**
   * 接收标本
   */
  async receiveSample(id: number, technicianId: number, technicianName: string) {
    try {
      const response = await sampleApi.receiveSample(id, {
        technicianId,
        technicianName
      })
      return response.data
    } catch (error) {
      console.error('接收标本失败:', error)
      throw error
    }
  }

  /**
   * 开始检验
   */
  async startTest(id: number, technicianId: number, technicianName: string) {
    try {
      const response = await sampleApi.startTest(id, {
        technicianId,
        technicianName
      })
      return response.data
    } catch (error) {
      console.error('开始检验失败:', error)
      throw error
    }
  }

  /**
   * 完成检验
   */
  async completeTest(id: number, technicianId: number, technicianName: string) {
    try {
      const response = await sampleApi.completeTest(id, {
        technicianId,
        technicianName
      })
      return response.data
    } catch (error) {
      console.error('完成检验失败:', error)
      throw error
    }
  }

  /**
   * 获取标本追踪记录
   */
  async getTraceRecords(id: number) {
    try {
      const response = await sampleApi.getTraceRecords(id)
      return response.data || []
    } catch (error) {
      console.error('获取追踪记录失败:', error)
      return []
    }
  }

  /**
   * 根据状态获取标本列表
   */
  async getSamplesByStatus(status: SampleStatus) {
    try {
      const response = await sampleApi.listByStatus(status)
      return response.data || []
    } catch (error) {
      console.error('按状态获取标本列表失败:', error)
      return []
    }
  }
}

// 导出单例实例
const sampleService = new SampleService()
export default sampleService
