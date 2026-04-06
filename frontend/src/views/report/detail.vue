<template>
  <div class="professional-report-detail-container">
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
          打印
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          导出PDF
        </el-button>
      </div>
    </div>

    <!-- 报告概览 -->
    <el-card shadow="hover" class="overview-card">
      <div class="report-header">
        <div class="report-info">
          <div class="report-no">
            <el-icon><Document /></el-icon>
            <span>{{ reportInfo.reportNo }}</span>
          </div>
          <div class="report-status">
            <el-tag :type="getStatusTagType(reportInfo.status)" size="large" effect="dark">
              {{ getStatusText(reportInfo.status) }}
            </el-tag>
            <el-tag v-if="reportInfo.priority === 'HIGH'" type="danger" size="large">
              <el-icon><Top /></el-icon> 紧急
            </el-tag>
          </div>
        </div>
        <div class="report-meta">
          <span><el-icon><Clock /></el-icon> {{ formatDate(reportInfo.createTime) }}</span>
          <span><el-icon><User /></el-icon> {{ reportInfo.createBy || '系统' }}</span>
        </div>
      </div>
    </el-card>

    <!-- 审核进度 -->
    <el-card shadow="hover" class="progress-card">
      <template #header>
        <div class="card-header">
          <el-icon><TrendCharts /></el-icon>
          <span>审核进度</span>
        </div>
      </template>
      <el-steps :active="getReviewStep(reportInfo.status)" align-center finish-status="success">
        <el-step title="创建报告" :description="reportInfo.createTime || ''" />
        <el-step title="技术审核" :description="reportInfo.technicalReviewTime || '-'" />
        <el-step title="医师审核" :description="reportInfo.clinicalReviewTime || '-'" />
        <el-step title="发布报告" :description="reportInfo.publishTime || '-'" />
      </el-steps>
    </el-card>

    <!-- 主体内容 -->
    <div class="content-grid">
      <!-- 左侧 -->
      <div class="left-column">
        <!-- 患者信息 -->
        <el-card shadow="hover" class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon><User /></el-icon>
              <span>患者信息</span>
            </div>
          </template>
          <div class="patient-profile">
            <el-avatar :size="56" class="patient-avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
            <div class="patient-details">
              <div class="patient-name">{{ reportInfo.patientName || '未知' }}</div>
              <div class="patient-meta">
                <span>ID: {{ reportInfo.patientId || '-' }}</span>
                <span>{{ reportInfo.gender === 'M' ? '男' : '女' }}</span>
                <span>{{ reportInfo.age || '-' }}岁</span>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 关联标本 -->
        <el-card shadow="hover" class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon><Box /></el-icon>
              <span>关联标本</span>
            </div>
          </template>
          <div class="sample-info">
            <el-tag size="large">{{ reportInfo.sampleNo || '-' }}</el-tag>
            <el-button type="primary" size="small" plain @click="viewSample">查看标本</el-button>
          </div>
        </el-card>

        <!-- 审核信息 -->
        <el-card shadow="hover" class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon><CircleCheck /></el-icon>
              <span>审核信息</span>
            </div>
          </template>
          <div class="review-list">
            <div class="review-item">
              <div class="review-label">技术审核</div>
              <div class="review-info">
                <span>{{ reportInfo.technicalReviewer || '待审核' }}</span>
                <span class="review-time">{{ reportInfo.technicalReviewTime || '-' }}</span>
              </div>
              <div class="review-status">
                <el-tag v-if="reportInfo.technicalReviewStatus === 'APPROVED'" type="success" size="small">通过</el-tag>
                <el-tag v-else type="info" size="small">待审核</el-tag>
              </div>
            </div>
            <div class="review-item">
              <div class="review-label">医师审核</div>
              <div class="review-info">
                <span>{{ reportInfo.clinicalReviewer || '待审核' }}</span>
                <span class="review-time">{{ reportInfo.clinicalReviewTime || '-' }}</span>
              </div>
              <div class="review-status">
                <el-tag v-if="reportInfo.clinicalReviewStatus === 'APPROVED'" type="success" size="small">通过</el-tag>
                <el-tag v-else type="info" size="small">待审核</el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧 -->
      <div class="right-column">
        <!-- 检验结果 -->
        <el-card shadow="hover" class="results-card">
          <template #header>
            <div class="card-header">
              <el-icon><Box /></el-icon>
              <span>检验结果</span>
              <el-tag type="info" size="small">{{ testResults.length }} 项</el-tag>
            </div>
          </template>
          <el-table :data="testResults" border stripe>
            <el-table-column prop="itemName" label="检验项目" min-width="150" />
            <el-table-column prop="result" label="结果" width="120">
              <template #default="{ row }">
                <span :class="getResultClass(row.flag)">{{ row.result }} {{ row.unit }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="reference" label="参考值" width="150" />
            <el-table-column prop="flag" label="标志" width="80">
              <template #default="{ row }">
                <el-tag v-if="row.flag && row.flag !== 'N'" :type="getFlagTagType(row.flag)" size="small">
                  {{ row.flag }}
                </el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 诊断建议 -->
        <el-card shadow="hover" class="diagnosis-card" v-if="reportInfo.diagnosis">
          <template #header>
            <div class="card-header">
              <el-icon><MagicStick /></el-icon>
              <span>诊断意见</span>
            </div>
          </template>
          <div class="diagnosis-content">
            <p>{{ reportInfo.diagnosis }}</p>
          </div>
        </el-card>

        <!-- 备注 -->
        <el-card shadow="hover" class="remark-card" v-if="reportInfo.remark">
          <template #header>
            <div class="card-header">
              <el-icon><Comment /></el-icon>
              <span>备注说明</span>
            </div>
          </template>
          <div class="remark-content">
            <p>{{ reportInfo.remark }}</p>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 底部操作 -->
    <div class="action-bar" v-if="canReview">
      <el-card shadow="hover" class="action-card">
        <div class="action-content">
          <div class="action-title">报告操作</div>
          <div class="action-buttons">
            <el-button type="success" size="large" @click="handleApprove" v-if="canApprove">
              <el-icon><CircleCheck /></el-icon>
              审核通过
            </el-button>
            <el-button type="danger" size="large" @click="handleReject" v-if="canReject">
              <el-icon><CloseBold /></el-icon>
              驳回
            </el-button>
            <el-button type="primary" size="large" @click="handlePublish" v-if="canPublish">
              <el-icon><Finished /></el-icon>
              发布报告
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 驳回对话框 -->
    <el-dialog v-model="rejectDialogVisible" title="驳回报告" width="500px">
      <el-form :model="rejectForm" label-width="100px">
        <el-form-item label="驳回原因">
          <el-input v-model="rejectForm.reason" type="textarea" :rows="4" placeholder="请输入驳回原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="submitReject">确认驳回</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft, Document, Printer, Download, Clock, User, Box, CircleCheck,
  Top, TrendCharts, MagicStick, Comment, CloseBold, Finished
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 报告信息
const reportInfo = ref({
  id: 1,
  reportNo: 'RPT2026032901',
  status: 'TECHNICAL_REVIEW',
  priority: 'NORMAL',
  patientName: '张三',
  patientId: 'P001',
  gender: 'M',
  age: 45,
  sampleNo: 'S2026032901',
  createTime: '2026-03-29 10:30:00',
  createBy: '李技师',
  technicalReviewer: '王医生',
  technicalReviewTime: '2026-03-29 11:00:00',
  technicalReviewStatus: 'APPROVED',
  clinicalReviewer: '',
  clinicalReviewTime: '',
  clinicalReviewStatus: '',
  publishTime: '',
  diagnosis: '血常规检查结果大致正常，肝功能检测显示轻度异常，建议复查。',
  remark: '患者有轻微感冒症状，不影响检验结果。'
})

// 检验结果
const testResults = ref([
  { itemName: '白细胞计数(WBC)', result: '6.5', unit: '×10⁹/L', reference: '4.0-10.0', flag: 'N' },
  { itemName: '红细胞计数(RBC)', result: '4.8', unit: '×10¹²/L', reference: '4.0-5.5', flag: 'N' },
  { itemName: '血红蛋白(HGB)', result: '142', unit: 'g/L', reference: '120-160', flag: 'N' },
  { itemName: '血小板计数(PLT)', result: '220', unit: '×10⁹/L', reference: '100-300', flag: 'N' },
  { itemName: '谷丙转氨酶(ALT)', result: '52', unit: 'U/L', reference: '0-40', flag: 'H' },
  { itemName: '谷草转氨酶(AST)', result: '38', unit: 'U/L', reference: '0-40', flag: 'N' }
])

// 驳回对话框
const rejectDialogVisible = ref(false)
const rejectForm = reactive({
  reason: ''
})

// 状态映射
const statusMap = {
  PENDING: { text: '待审核', type: 'info' },
  TECHNICAL_REVIEW: { text: '技术审核中', type: 'warning' },
  CLINICAL_REVIEW: { text: '医师审核中', type: 'warning' },
  APPROVED: { text: '已通过', type: 'success' },
  PUBLISHED: { text: '已发布', type: 'success' },
  REJECTED: { text: '已驳回', type: 'danger' }
}

// 计算属性
const canReview = computed(() => ['PENDING', 'TECHNICAL_REVIEW', 'CLINICAL_REVIEW'].includes(reportInfo.value.status))
const canApprove = computed(() => ['PENDING', 'TECHNICAL_REVIEW', 'CLINICAL_REVIEW'].includes(reportInfo.value.status))
const canReject = computed(() => ['PENDING', 'TECHNICAL_REVIEW', 'CLINICAL_REVIEW'].includes(reportInfo.value.status))
const canPublish = computed(() => reportInfo.value.status === 'APPROVED')

// 获取状态文本
const getStatusText = (status) => statusMap[status]?.text || status

// 获取状态标签类型
const getStatusTagType = (status) => statusMap[status]?.type || 'info'

// 获取审核步骤
const getReviewStep = (status) => {
  const steps = { PENDING: 0, TECHNICAL_REVIEW: 1, CLINICAL_REVIEW: 2, APPROVED: 3, PUBLISHED: 4, REJECTED: 0 }
  return steps[status] || 0
}

// 获取结果样式
const getResultClass = (flag) => {
  if (flag === 'H' || flag === 'HH') return 'result-high'
  if (flag === 'L' || flag === 'LL') return 'result-low'
  return ''
}

// 获取标志标签类型
const getFlagTagType = (flag) => {
  if (flag === 'H' || flag === 'HH') return 'danger'
  if (flag === 'L' || flag === 'LL') return 'warning'
  return 'info'
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

// 返回
const goBack = () => { router.push('/report') }

// 打印
const handlePrint = () => { ElMessage.info('正在准备打印...') }

// 导出
const handleExport = () => { ElMessage.info('正在导出PDF...') }

// 查看标本
const viewSample = () => { router.push(`/sample/detail/${reportInfo.value.sampleId}`) }

// 审核通过
const handleApprove = () => {
  ElMessageBox.confirm('确定审核通过该报告吗？', '审核确认', { type: 'success' })
    .then(() => {
      ElMessage.success('审核通过')
      reportInfo.value.status = 'APPROVED'
    }).catch(() => {})
}

// 驳回
const handleReject = () => {
  rejectDialogVisible.value = true
}

// 提交驳回
const submitReject = () => {
  if (!rejectForm.reason) {
    ElMessage.warning('请输入驳回原因')
    return
  }
  ElMessage.success('报告已驳回')
  rejectDialogVisible.value = false
  reportInfo.value.status = 'REJECTED'
}

// 发布
const handlePublish = () => {
  ElMessageBox.confirm('确定发布该报告吗？发布后将无法修改。', '发布确认', { type: 'warning' })
    .then(() => {
      ElMessage.success('报告已发布')
      reportInfo.value.status = 'PUBLISHED'
    }).catch(() => {})
}

onMounted(() => {})
</script>

<style scoped>
.professional-report-detail-container {
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ed 100%);
  min-height: 100%;
}

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

.overview-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.report-no {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.report-status {
  display: flex;
  gap: 8px;
}

.report-meta {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #909399;
}

.report-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.progress-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 20px;
  margin-bottom: 20px;
}

.info-card, .results-card, .diagnosis-card, .remark-card {
  border-radius: 12px;
  margin-bottom: 16px;
}

.patient-profile {
  display: flex;
  align-items: center;
  gap: 16px;
}

.patient-avatar {
  background: linear-gradient(135deg, #67C23A, #85ce61);
  font-size: 24px;
}

.patient-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.patient-meta {
  display: flex;
  gap: 12px;
  font-size: 14px;
  color: #606266;
}

.sample-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.review-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.review-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.review-label {
  width: 80px;
  font-weight: 600;
  color: #303133;
}

.review-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  font-size: 13px;
  color: #606266;
}

.review-time {
  color: #909399;
  font-size: 12px;
}

.result-high, .result-low {
  font-weight: 600;
}

.result-high { color: #F56C6C; }
.result-low { color: #E6A23C; }

.diagnosis-content, .remark-content {
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
}

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

@media (max-width: 1200px) {
  .content-grid { grid-template-columns: 1fr; }
}
</style>
