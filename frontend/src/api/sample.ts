import Request from '@/utils/request'
import type { ApiResponse, Sample, PageParams, PageResult, SampleStatus } from '@/types'

export interface UpdateStatusParams {
  status: SampleStatus
  operatorId?: number
  operatorName?: string
  location?: string
}

export interface ReceiveSampleParams {
  technicianId: number
  technicianName: string
}

export const sampleApi = {
  // 创建标本
  createSample: (data: Partial<Sample>): Promise<ApiResponse<Sample>> => {
    return Request.post('/sample/create', data)
  },

  // 根据ID获取标本
  getSampleById: (id: number): Promise<ApiResponse<Sample>> => {
    return Request.get(`/sample/${id}`)
  },

  // 扫码查询标本
  scanSample: (sampleNo: string): Promise<ApiResponse<Sample>> => {
    return Request.get(`/sample/scan/${sampleNo}`)
  },

  // 更新标本状态
  updateStatus: (id: number, data: UpdateStatusParams): Promise<ApiResponse<Sample>> => {
    return Request.post(`/sample/${id}/status`, data)
  },

  // 接收标本
  receiveSample: (id: number, data: ReceiveSampleParams): Promise<ApiResponse<Sample>> => {
    return Request.post(`/sample/${id}/receive`, null, { params: data })
  },

  // 开始检验
  startTest: (id: number, data: ReceiveSampleParams): Promise<ApiResponse<Sample>> => {
    return Request.post(`/sample/${id}/start-test`, null, { params: data })
  },

  // 完成检验
  completeTest: (id: number, data: ReceiveSampleParams): Promise<ApiResponse<Sample>> => {
    return Request.post(`/sample/${id}/complete`, null, { params: data })
  },

  // 获取标本追踪记录
  getTraceRecords: (id: number): Promise<ApiResponse<any[]>> => {
    return Request.get(`/sample/${id}/traces`)
  },

  // 获取所有标本
  listSamples: (params?: PageParams): Promise<ApiResponse<PageResult<Sample>>> => {
    return Request.get('/sample/list', { params })
  },

  // 根据状态获取标本列表
  listByStatus: (status: SampleStatus): Promise<ApiResponse<Sample[]>> => {
    return Request.get('/sample/list-by-status', { params: { status } })
  }
}
