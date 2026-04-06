import Request from '@/utils/request'
import type { ApiResponse, Report, PageParams, PageResult, TestResult } from '@/types'

export interface InputResultsParams {
  results: Partial<TestResult>[]
  technicianId: number
  technicianName: string
}

export interface ReviewReportParams {
  reviewerId: number
  reviewerName: string
  approved: boolean
  remark?: string
}

export const reportApi = {
  // 创建报告
  createReport: (data: Partial<Report>): Promise<ApiResponse<Report>> => {
    return Request.post('/report/create', data)
  },

  // 根据ID获取报告
  getReportById: (id: number): Promise<ApiResponse<Report>> => {
    return Request.get(`/report/${id}`)
  },

  // 根据报告编号查询
  getReportByNo: (reportNo: string): Promise<ApiResponse<Report>> => {
    return Request.get(`/report/no/${reportNo}`)
  },

  // 录入检验结果
  inputResults: (id: number, data: InputResultsParams): Promise<ApiResponse<Report>> => {
    return Request.post(`/report/${id}/input-results`, data)
  },

  // 审核报告
  reviewReport: (id: number, data: ReviewReportParams): Promise<ApiResponse<Report>> => {
    return Request.post(`/report/${id}/review`, data)
  },

  // 发布报告
  publishReport: (id: number): Promise<ApiResponse<Report>> => {
    return Request.post(`/report/${id}/publish`)
  },

  // 根据患者ID查询报告
  getReportsByPatientId: (patientId: number): Promise<ApiResponse<Report[]>> => {
    return Request.get(`/report/patient/${patientId}`)
  },

  // 获取待审核报告列表
  getPendingReports: (): Promise<ApiResponse<Report[]>> => {
    return Request.get('/report/pending-list')
  },

  // 获取所有报告（分页）
  listReports: (params?: PageParams): Promise<ApiResponse<PageResult<Report>>> => {
    return Request.get('/report/list', { params })
  }
}
