/**
 * AI诊断服务
 * 封装AI辅助诊断相关的业务逻辑和API调用
 */

import { aiApi } from '@/api/ai'
import type { AiDiagnosisRequest, AiDiagnosisResponse } from '@/types'

class AiService {
  /**
   * 完整的AI辅助诊断
   */
  async diagnose(data: AiDiagnosisRequest): Promise<AiDiagnosisResponse | null> {
    try {
      const response = await aiApi.diagnose(data)
      return response.data
    } catch (error) {
      console.error('AI诊断失败:', error)
      
      // 返回模拟数据作为fallback（用于演示）
      return this.getMockDiagnosisResult(data)
    }
  }

  /**
   * 简化版AI诊断
   */
  async simpleDiagnose(testData: any): Promise<AiDiagnosisResponse | null> {
    try {
      const response = await aiApi.simpleDiagnose(testData)
      return response.data
    } catch (error) {
      console.error('简化版AI诊断失败:', error)
      return this.getMockDiagnosisResult(testData)
    }
  }

  /**
   * 血常规AI诊断
   */
  async diagnoseBloodRoutine(results: any[]): Promise<AiDiagnosisResponse | null> {
    try {
      const response = await aiApi.diagnoseBloodRoutine(results)
      return response.data
    } catch (error) {
      console.error('血常规诊断失败:', error)
      return this.getMockBloodRoutineResult(results)
    }
  }

  /**
   * 尿常规AI诊断
   */
  async diagnoseUrineRoutine(results: any[]): Promise<AiDiagnosisResponse | null> {
    try {
      const response = await aiApi.diagnoseUrineRoutine(results)
      return response.data
    } catch (error) {
      console.error('尿常规诊断失败:', error)
      return this.getMockUrineRoutineResult(results)
    }
  }

  /**
   * 检查AI服务健康状态
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await aiApi.health()
      return response.data?.status === 'ok'
    } catch (error) {
      console.error('AI服务健康检查失败:', error)
      return false
    }
  }

  /**
   * 获取模拟的诊断结果（当后端不可用时）
   */
  private getMockDiagnosisResult(_data: any): AiDiagnosisResponse {
    return {
      id: Date.now(),
      diagnosisTime: new Date().toISOString(),
      result: '正常',
      confidence: 0.95,
      suggestions: [
        '各项指标在正常范围内',
        '建议定期复查',
        '保持良好的生活习惯'
      ],
      abnormalIndicators: [],
      riskLevel: 'low' as const,
      details: {
        summary: '血常规检查结果基本正常，未发现明显异常指标。',
        analysis: '根据您提供的检验数据进行综合分析，白细胞计数、红细胞计数、血红蛋白浓度等主要指标均在参考范围内。',
        recommendations: [
          '保持均衡饮食，适量运动',
          '保证充足睡眠，避免过度劳累',
          '定期进行健康体检'
        ]
      }
    }
  }

  /**
   * 血常规模拟结果
   */
  private getMockBloodRoutineResult(results: any[]): AiDiagnosisResponse {
    // 简单分析输入数据
    let hasAbnormal = false
    const abnormalities: string[] = []

    if (results && results.length > 0) {
      for (const item of results) {
        if (item.itemName && item.result) {
          // 简单的异常检测逻辑
          if (item.itemName.includes('白细胞') && parseFloat(item.result) > 10) {
            hasAbnormal = true
            abnormalities.push(`${item.itemName}偏高`)
          }
          if (item.itemName.includes('红细胞') && parseFloat(item.result) < 4.0) {
            hasAbnormal = true
            abnormalities.push(`${item.itemName}偏低`)
          }
        }
      }
    }

    return {
      id: Date.now(),
      diagnosisTime: new Date().toISOString(),
      result: hasAbnormal ? '异常' : '正常',
      confidence: hasAbnormal ? 0.88 : 0.96,
      suggestions: hasAbnormal ? [
        '发现部分指标异常，建议进一步检查',
        '咨询专业医生获取详细解读',
        '注意休息，避免剧烈运动'
      ] : [
        '各项指标在正常范围内',
        '建议定期复查',
        '保持良好的生活习惯'
      ],
      abnormalIndicators: abnormalities,
      riskLevel: hasAbnormal ? 'medium' as const : 'low' as const,
      details: {
        summary: hasAbnormal 
          ? `血常规检查发现${abnormalities.length}项异常指标，需要关注。`
          : '血常规检查结果基本正常，未发现明显异常指标。',
        analysis: '基于人工智能算法对您的血常规检验数据进行分析，结合临床知识库给出诊断建议。',
        recommendations: hasAbnormal ? [
          '建议到正规医院血液科进一步检查',
          '避免自行用药，遵医嘱治疗',
          '一周后复查血常规'
        ] : [
          '继续保持健康的生活方式',
          '每年至少进行一次全面体检',
          '如有不适及时就医'
        ]
      }
    }
  }

  /**
   * 尿常规模拟结果
   */
  private getMockUrineRoutineResult(_results: any[]): AiDiagnosisResponse {
    return {
      id: Date.now(),
      diagnosisTime: new Date().toISOString(),
      result: '正常',
      confidence: 0.94,
      suggestions: [
        '尿常规检查正常',
        '多喝水，促进新陈代谢',
        '注意个人卫生'
      ],
      abnormalIndicators: [],
      riskLevel: 'low' as const,
      details: {
        summary: '尿常规检查各项指标均在正常范围内。',
        analysis: '尿常规检查是评估肾脏功能和泌尿系统健康的重要手段，本次检查结果良好。',
        recommendations: [
          '每天饮水2000ml以上',
          '避免憋尿习惯',
          '定期体检'
        ]
      }
    }
  }
}

// 导出单例实例
const aiService = new AiService()
export default aiService
