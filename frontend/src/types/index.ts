// 通用API响应类型
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 分页查询参数
export interface PageParams {
  page: number
  pageSize: number
  [key: string]: any
}

// 分页响应数据
export interface PageResult<T = any> {
  list: T[]
  total: number
  page: number
  pageSize: number
}

// 用户角色类型
export type UserRole = 'ADMIN' | 'TECHNICIAN' | 'LAB_TECHNICIAN' | 'DOCTOR' | 'NURSE' | 'USER'

// 用户角色显示名称映射
export const UserRoleLabels: Record<UserRole, string> = {
  'ADMIN': '系统管理员',
  'TECHNICIAN': '检验技师',
  'LAB_TECHNICIAN': '检验技师',
  'DOCTOR': '医生',
  'NURSE': '护士',
  'USER': '普通用户'
}

// 用户信息类型
export interface User {
  id?: number
  username: string
  password?: string
  realName?: string
  email?: string
  phone?: string
  role: UserRole
  status?: number
  createTime?: string
  updateTime?: string
}

// 登录请求参数
export interface LoginParams {
  username: string
  password: string
}

// 登录响应数据
export interface LoginResponse {
  token: string
  user: User
}

// 标本状态类型
export type SampleStatus = 
  | 'PENDING' 
  | 'PROCESSING' 
  | 'TESTING' 
  | 'COMPLETED' 
  | 'REJECTED'

// 标本类型
export interface SampleType {
  id?: number
  code: string
  name: string
  description?: string
}

// 患者信息
export interface Patient {
  id?: number
  patientNo: string
  name: string
  gender?: 'MALE' | 'FEMALE'
  age?: number
  phone?: string
  idCard?: string
  address?: string
  createTime?: string
}

// 标本信息
export interface Sample {
  id?: number
  sampleNo: string
  patientId?: number
  patient?: Patient
  sampleTypeId?: number
  sampleType?: SampleType
  collectionTime?: string
  receivedTime?: string
  status: SampleStatus
  remarks?: string
  createTime?: string
  updateTime?: string
}

// 报告状态
export type ReportStatus = 'DRAFT' | 'PENDING_REVIEW' | 'REVIEWED' | 'PUBLISHED'

// 检验项目
export interface TestItem {
  id?: number
  code: string
  name: string
  unit?: string
  referenceRange?: string
  department?: string
}

// 检验结果
export interface TestResult {
  id?: number
  reportId?: number
  testItemId?: number
  testItem?: TestItem
  value?: string
  unit?: string
  referenceRange?: string
  isAbnormal?: boolean
  abnormalFlag?: string
  remark?: string
}

// 报告信息
export interface Report {
  id?: number
  reportNo: string
  sampleId?: number
  sample?: Sample
  patientId?: number
  patient?: Patient
  status: ReportStatus
  testResults?: TestResult[]
  diagnosis?: string
  conclusion?: string
  technicianId?: number
  technician?: User
  reviewerId?: number
  reviewer?: User
  reviewTime?: string
  publishTime?: string
  createTime?: string
  updateTime?: string
}

// AI诊断请求
export interface AiDiagnosisRequest {
  symptoms?: string
  testResults?: string
  medicalHistory?: string
}

// AI诊断响应
export interface AiDiagnosisResponse {
  id?: number
  diagnosisTime?: string
  result?: string
  diagnosis?: string
  suggestions: string[]
  confidence: number
  abnormalIndicators?: string[]
  riskLevel?: 'low' | 'medium' | 'high'
  details?: {
    summary: string
    analysis: string
    recommendations: string[]
  }
}

// 仪表盘统计数据
export interface DashboardStats {
  totalSamples: number
  pendingSamples: number
  completedReports: number
  pendingReviews: number
  sampleStatusStats: {
    status: string
    count: number
  }[]
  recentActivities: {
    id: number
    type: string
    content: string
    time: string
  }[]
}
