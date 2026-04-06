import Request from '@/utils/request'
import type { ApiResponse, AiDiagnosisRequest, AiDiagnosisResponse } from '@/types'

export const aiApi = {
  // AI辅助诊断（完整版）
  diagnose: (data: AiDiagnosisRequest): Promise<ApiResponse<AiDiagnosisResponse>> => {
    return Request.post('/ai/diagnose', data)
  },

  // 简化版诊断（供其他服务调用）
  simpleDiagnose: (testData: any): Promise<ApiResponse<AiDiagnosisResponse>> => {
    return Request.post('/ai/simple-diagnose', testData)
  },

  // 血常规诊断
  diagnoseBloodRoutine: (results: any[]): Promise<ApiResponse<AiDiagnosisResponse>> => {
    return Request.post('/ai/diagnose/blood-routine', results)
  },

  // 尿常规诊断
  diagnoseUrineRoutine: (results: any[]): Promise<ApiResponse<AiDiagnosisResponse>> => {
    return Request.post('/ai/diagnose/urine-routine', results)
  },

  // 健康检查
  health: (): Promise<ApiResponse<{ status: string }>> => {
    return Request.get('/ai/health')
  }
}
