<template>
  <div class="professional-detail-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回列表
        </el-button>
      </div>
      <div class="header-right">
        <el-button @click="handlePrint">
          <el-icon><Printer /></el-icon>
          打印标签
        </el-button>
        <el-button type="primary" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <!-- 标本概览卡片 -->
    <div class="overview-cards">
      <el-card class="overview-card main-card">
        <div class="sample-header">
          <div class="sample-info">
            <div class="sample-no">
              <el-icon><Document /></el-icon>
              <span>{{ sampleInfo.sampleNo }}</span>
            </div>
            <div class="sample-status">
              <el-tag :type="getStatusTagType(sampleInfo.status)" size="large" effect="dark">
                {{ getStatusText(sampleInfo.status) }}
              </el-tag>
              <el-tag v-if="sampleInfo.priority === 'HIGH'" type="danger" size="large">
                <el-icon><Top /></el-icon> 紧急
              </el-tag>
            </div>
          </div>
          <div class="sample-meta">
            <span class="meta-item">
              <el-icon><Clock /></el-icon>
              创建于 {{ formatDate(sampleInfo.createTime) }}
            </span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 主体内容 -->
    <div class="content-grid">
      <!-- 左侧列 -->
      <div class="left-column">
        <!-- 基本信息 -->
        <el-card shadow="hover" class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon><InfoFilled /></el-icon>
              <span>基本信息</span>
            </div>
          </template>
          <div class="info-grid">
            <div class="info-item">
              <label>标本类型</label>
              <div class="info-value">
                <el-tag :type="getSampleTypeTag(sampleInfo.sampleType)">
                  {{ getSampleTypeText(sampleInfo.sampleType) }}
                </el-tag>
              </div>
            </div>
            <div class="info-item">
              <label>标本编号</label>
              <div class="info-value highlight">{{ sampleInfo.sampleNo }}</div>
            </div>
            <div class="info-item">
              <label>采集时间</label>
              <div class="info-value">{{ sampleInfo.collectTime || '-' }}</div>
            </div>
            <div class="info-item">
              <label>接收时间</label>
              <div class="info-value">{{ sampleInfo.receiveTime || '-' }}</div>
            </div>
          </div>
        </el-card>

        <!-- 患者信息 -->
        <el-card shadow="hover" class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon><User /></el-icon>
              <span>患者信息</span>
            </div>
          </template>
          <div class="patient-profile">
            <el-avatar :size="64" class="patient-avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
            <div class="patient-details">
              <div class="patient-name">{{ sampleInfo.patientName || '未知' }}</div>
              <div class="patient-meta">
                <span><el-icon><Postcard /></el-icon> ID: {{ sampleInfo.patientId || '-' }}</span>
                <span><el-icon><Male v-if="sampleInfo.gender === 'M'" /><Female v-else /></el-icon> {{ sampleInfo.gender === 'M' ? '男' : '女' }}</span>
                <span><el-icon><OfficeBuilding /></el-icon> {{ sampleInfo.patientAge || '-' }}岁</span>
              </div>
              <div class="patient-contact" v-if="sampleInfo.phone">
                <el-icon><Phone /></el-icon> {{ sampleInfo.phone }}
              </div>
            </div>
          </div>
        </el-card>

        <!-- 送检信息 -->
        <el-card shadow="hover" class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon><OfficeBuilding /></el-icon>
              <span>送检信息</span>
            </div>
          </template>
          <div class="info-grid">
            <div class="info-item">
              <label>送检科室</label>
              <div class="info-value">{{ sampleInfo.department || '-' }}</div>
            </div>
            <div class="info-item">
              <label>送检医生</label>
              <div class="info-value">{{ sampleInfo.doctor || '-' }}</div>
            </div>
            <div class="info-item full-width">
              <label>临床诊断</label>
              <div class="info-value">{{ sampleInfo.diagnosis || '-' }}</div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧列 -->
      <div class="right-column">
        <!-- 检验项目 -->
        <el-card shadow="hover" class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon><Box /></el-icon>
              <span>检验项目</span>
              <el-tag type="info" size="small">{{ sampleInfo.testItems?.length || 0 }} 项</el-tag>
            </div>
          </template>
          <div class="test-items-list">
            <div
              v-for="(item, index) in sampleInfo.testItems"
              :key="index"
              class="test-item"
            >
              <div class="test-item-index">{{ index + 1 }}</div>
              <div class="test-item-info">
                <div class="test-item-name">{{ item }}</div>
                <div class="test-item-status">
                  <el-tag v-if="getItemStatus(item) === 'completed'" type="success" size="small">
                    已完成
                  </el-tag>
                  <el-tag v-else-if="getItemStatus(item) === 'testing'" type="warning" size="small">
                    检验中
                  </el-tag>
                  <el-tag v-else type="info" size="small">
                    待检验
                  </el-tag>
                </div>
              </div>
              <div class="test-item-action">
                <el-button size="small" type="primary" plain>结果</el-button>
              </div>
            </div>
            <el-empty v-if="!sampleInfo.testItems || sampleInfo.testItems.length === 0" description="暂无检验项目" />
          </div>
        </el-card>

        <!-- 操作记录 -->
        <el-card shadow="hover" class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon><Timer /></el-icon>
              <span>操作记录</span>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(trace, index) in traceRecords"
              :key="index"
              :timestamp="trace.createTime"
              :type="getTraceType(trace.status)"
              :hollow="index === traceRecords.length - 1"
            >
              <div class="trace-item">
                <div class="trace-title">{{ getStatusText(trace.status) }}</div>
                <div class="trace-meta">
                  <span><el-icon><User /></el-icon> {{ trace.operatorName }}</span>
                  <span><el-icon><Location /></el-icon> {{ trace.location }}</span>
                </div>
                <div class="trace-remark" v-if="trace.remark">{{ trace.remark }}</div>
              </div>
            </el-timeline-item>
            <el-empty v-if="traceRecords.length === 0" description="暂无操作记录" />
          </el-timeline>
        </el-card>
      </div>
    </div>

    <!-- 底部操作区 -->
    <div class="action-bar">
      <el-card shadow="hover" class="action-card">
        <div class="action-content">
          <div class="action-title">标本操作</div>
          <div class="action-buttons">
            <el-button
              type="success"
              size="large"
              @click="handleReceiveSample"
              v-if="sampleInfo.status === 'PENDING' || sampleInfo.status === 'COLLECTED'"
            >
              <el-icon><Box /></el-icon>
              接收标本
            </el-button>
            <el-button
              type="warning"
              size="large"
              @click="handleStartTest"
              v-if="sampleInfo.status === 'RECEIVED'"
            >
              <el-icon><Loading /></el-icon>
              开始检验
            </el-button>
            <el-button
              type="primary"
              size="large"
              @click="handleCompleteTest"
              v-if="sampleInfo.status === 'TESTING'"
            >
              <el-icon><CircleCheck /></el-icon>
              完成检验
            </el-button>
            <el-button
              type="success"
              size="large"
              @click="handleCreateReport"
              v-if="sampleInfo.status === 'COMPLETED'"
            >
              <el-icon><Document /></el-icon>
              创建报告
            </el-button>
            <el-button
              type="danger"
              size="large"
              @click="handleMarkAbnormal"
              v-if="['RECEIVED', 'TESTING'].includes(sampleInfo.status)"
            >
              <el-icon><WarningFilled /></el-icon>
              标记异常
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 异常标记对话框 -->
    <el-dialog v-model="abnormalDialogVisible" title="标记异常" width="500px">
      <el-form :model="abnormalForm" label-width="100px">
        <el-form-item label="异常类型">
          <el-select v-model="abnormalForm.type" placeholder="请选择异常类型" style="width: 100%">
            <el-option label="标本损坏" value="DAMAGED" />
            <el-option label="标本量不足" value="INSUFFICIENT" />
            <el-option label="信息错误" value="INFO_ERROR" />
            <el-option label="检验结果异常" value="RESULT_ABNORMAL" />
            <el-option label="其他" value="OTHER" />
          </el-select>
        </el-form-item>
        <el-form-item label="异常描述">
          <el-input v-model="abnormalForm.remark" type="textarea" :rows="4" placeholder="请输入异常描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="abnormalDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="submitAbnormal">确认标记</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft, Document, Printer, Download, InfoFilled, User, Postcard,
  Phone, Male, Female, OfficeBuilding, Box, Timer, Location,
  Clock, Top, CircleCheck, Loading, WarningFilled
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 标本信息
const sampleInfo = ref({
  id: 1,
  sampleNo: 'S2026032901',
  sampleType: 'blood',
  priority: 'NORMAL',
  status: 'TESTING',
  patientName: '张三',
  patientId: 'P001',
  gender: 'M',
  patientAge: 45,
  phone: '13800138000',
  department: '内科',
  doctor: '李医生',
  diagnosis: '常规体检',
  collectTime: '2026-03-29 08:30:00',
  receiveTime: '2026-03-29 09:00:00',
  testItems: ['血常规检查', '肝功能检测', '血糖测定', '血脂分析'],
  createTime: '2026-03-29 08:30:00'
})

// 操作记录
const traceRecords = ref([
  { status: 'TESTING', operatorName: '王技师', location: '检验科', createTime: '2026-03-29 09:30:00', remark: '开始进行检验' },
  { status: 'RECEIVED', operatorName: '张护士', location: '检验科', createTime: '2026-03-29 09:00:00', remark: '标本已接收' },
  { status: 'COLLECTED', operatorName: '李护士', location: '门诊', createTime: '2026-03-29 08:30:00', remark: '标本采集完成' }
])

// 异常对话框
const abnormalDialogVisible = ref(false)
const abnormalForm = reactive({
  type: '',
  remark: ''
})

// 状态映射
const statusMap = {
  PENDING: { text: '待接收', type: 'info' },
  COLLECTED: { text: '已采集', type: 'primary' },
  RECEIVED: { text: '已接收', type: 'success' },
  TESTING: { text: '检验中', type: 'warning' },
  COMPLETED: { text: '已完成', type: 'success' },
  ABNORMAL: { text: '异常', type: 'danger' },
  ARCHIVED: { text: '已归档', type: 'info' }
}

const sampleTypeMap = {
  blood: { text: '血液', type: 'danger' },
  urine: { text: '尿液', type: 'success' },
  secretion: { text: '分泌物', type: 'warning' },
  tissue: { text: '组织', type: 'info' },
  other: { text: '其他', type: '' }
}

// 获取状态文本
const getStatusText = (status) => statusMap[status]?.text || status

// 获取状态标签类型
const getStatusTagType = (status) => statusMap[status]?.type || 'info'

// 获取标本类型文本
const getSampleTypeText = (type) => sampleTypeMap[type]?.text || type

// 获取标本类型标签
const getSampleTypeTag = (type) => sampleTypeMap[type]?.type || 'info'

// 获取检验项目状态
const getItemStatus = (item) => {
  // 模拟状态
  const completed = ['血常规检查', '肝功能检测']
  const testing = ['血糖测定']
  if (completed.includes(item)) return 'completed'
  if (testing.includes(item)) return 'testing'
  return 'pending'
}

// 获取追踪类型
const getTraceType = (status) => statusMap[status]?.type || 'info'

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 返回列表
const goBack = () => {
  router.push('/sample')
}

// 打印
const handlePrint = () => {
  ElMessage.info('正在准备打印标签...')
}

// 导出
const handleExport = () => {
  ElMessage.info('正在导出标本信息...')
}

// 接收标本
const handleReceiveSample = () => {
  ElMessageBox.confirm('确定接收该标本吗？', '接收确认', { type: 'success' })
    .then(() => {
      ElMessage.success('标本已接收')
      sampleInfo.value.status = 'RECEIVED'
    })
    .catch(() => {})
}

// 开始检验
const handleStartTest = () => {
  ElMessageBox.confirm('确定开始检验该标本吗？', '开始检验', { type: 'warning' })
    .then(() => {
      ElMessage.success('已开始检验')
      sampleInfo.value.status = 'TESTING'
    })
    .catch(() => {})
}

// 完成检验
const handleCompleteTest = () => {
  ElMessageBox.confirm('确定完成检验吗？', '完成确认', { type: 'success' })
    .then(() => {
      ElMessage.success('检验已完成')
      sampleInfo.value.status = 'COMPLETED'
    })
    .catch(() => {})
}

// 创建报告
const handleCreateReport = () => {
  router.push(`/report/create?sampleId=${sampleInfo.value.id}`)
}

// 标记异常
const handleMarkAbnormal = () => {
  abnormalDialogVisible.value = true
}

// 提交异常
const submitAbnormal = () => {
  if (!abnormalForm.type) {
    ElMessage.warning('请选择异常类型')
    return
  }
  ElMessage.success('已标记为异常')
  abnormalDialogVisible.value = false
  sampleInfo.value.status = 'ABNORMAL'
}

// 生命周期
onMounted(() => {
  // 加载数据
})
</script>

<style scoped>
.professional-detail-container {
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ed 100%);
  min-height: 100%;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.header-right {
  display: flex;
  gap: 12px;
}

/* 概览卡片 */
.overview-cards {
  margin-bottom: 20px;
}

.overview-card.main-card {
  border-radius: 12px;
}

.sample-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.sample-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.sample-no {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.sample-status {
  display: flex;
  gap: 8px;
}

.sample-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #909399;
}

/* 内容网格 */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.info-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item.full-width {
  grid-column: span 2;
}

.info-item label {
  font-size: 13px;
  color: #909399;
}

.info-value {
  font-size: 15px;
  color: #303133;
}

.info-value.highlight {
  font-weight: 600;
  color: #409EFF;
}

/* 患者信息 */
.patient-profile {
  display: flex;
  align-items: center;
  gap: 20px;
}

.patient-avatar {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  font-size: 28px;
}

.patient-details {
  flex: 1;
}

.patient-name {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.patient-meta {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
}

.patient-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.patient-contact {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #909399;
}

/* 检验项目 */
.test-items-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.test-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  transition: all 0.2s;
}

.test-item:hover {
  background: #ecf5ff;
}

.test-item-index {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.test-item-info {
  flex: 1;
}

.test-item-name {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
}

/* 操作记录 */
.trace-item {
  padding: 4px 0;
}

.trace-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.trace-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.trace-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.trace-remark {
  margin-top: 4px;
  font-size: 12px;
  color: #606266;
}

/* 底部操作区 */
.action-bar {
  margin-top: 20px;
}

.action-card {
  border-radius: 12px;
}

.action-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

/* 响应式 */
@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .info-item.full-width {
    grid-column: span 1;
  }
  
  .action-buttons {
    flex-wrap: wrap;
  }
}
</style>
