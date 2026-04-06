<template>
  <div class="report-review-panel">
    <!-- 审核头部 -->
    <div class="review-header">
      <h3 class="panel-title">
        <el-icon><EditPen /></el-icon>
        报告审核
      </h3>
      <div class="report-info">
        <span class="report-no">报告编号：{{ report.reportNo }}</span>
        <el-tag :type="getStatusType(report.status)" size="small">
          {{ getStatusText(report.status) }}
        </el-tag>
      </div>
    </div>

    <!-- 审核内容区域 -->
    <div class="review-content">
      <!-- 左侧：报告详情 -->
      <div class="report-details">
        <div class="section">
          <h4 class="section-title">
            <el-icon><Document /></el-icon>
            报告内容
          </h4>
          <div class="section-content">
            <div v-if="report.content" class="report-content">
              {{ report.content }}
            </div>
            <div v-else class="empty-content">
              暂无报告内容
            </div>
          </div>
        </div>

        <div class="section">
          <h4 class="section-title">
            <el-icon><Cpu /></el-icon>
            AI诊断建议
          </h4>
          <div class="section-content">
            <div v-if="report.aiDiagnosis" class="ai-diagnosis">
              {{ report.aiDiagnosis }}
            </div>
            <div v-else class="empty-content">
              暂无AI诊断建议
            </div>
          </div>
        </div>

        <div class="section">
          <h4 class="section-title">
            <el-icon><Warning /></el-icon>
            异常提醒
          </h4>
          <div class="section-content">
            <div v-if="report.abnormalItems && report.abnormalItems.length > 0" class="abnormal-items">
              <div v-for="(item, index) in report.abnormalItems" :key="index" class="abnormal-item">
                <el-icon color="#f56c6c"><Warning /></el-icon>
                <span class="item-name">{{ item.name }}：</span>
                <span class="item-value">{{ item.value }}</span>
                <span class="item-range">（参考范围：{{ item.referenceRange }}）</span>
              </div>
            </div>
            <div v-else class="empty-content">
              无异常项目
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：审核操作 -->
      <div class="review-actions">
        <div class="action-section">
          <h4 class="section-title">
            <el-icon><Check /></el-icon>
            审核操作
          </h4>
          
          <!-- 审核状态 -->
          <div class="review-status">
            <div class="status-option">
              <el-radio-group v-model="reviewForm.status" size="large">
                <el-radio-button label="approved">
                  <el-icon><CircleCheck /></el-icon>
                  审核通过
                </el-radio-button>
                <el-radio-button label="rejected">
                  <el-icon><CircleClose /></el-icon>
                  审核不通过
                </el-radio-button>
                <el-radio-button label="pending">
                  <el-icon><Clock /></el-icon>
                  待修改
                </el-radio-button>
              </el-radio-group>
            </div>
          </div>

          <!-- 审核意见 -->
          <div class="review-comment">
            <div class="form-item">
              <label class="form-label">审核意见：</label>
              <el-input
                v-model="reviewForm.comment"
                type="textarea"
                :rows="4"
                placeholder="请输入审核意见"
                resize="none"
              />
            </div>
          </div>

          <!-- 电子签名 -->
          <div class="electronic-signature">
            <div class="form-item">
              <label class="form-label">电子签名：</label>
              <div class="signature-area">
                <div class="signature-preview">
                  <div class="signature-name">{{ userInfo.realName }}</div>
                  <div class="signature-role">{{ userInfo.role }}</div>
                  <div class="signature-time">{{ currentTime }}</div>
                </div>
                <el-checkbox v-model="reviewForm.signed" label="我已确认审核结果" />
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button
              type="primary"
              :loading="submitting"
              :disabled="!reviewForm.signed"
              @click="handleSubmitReview"
            >
              <el-icon><Check /></el-icon>
              提交审核
            </el-button>
            <el-button @click="handleSaveDraft">
              <el-icon><DocumentAdd /></el-icon>
              保存草稿
            </el-button>
            <el-button type="info" @click="handleViewHistory">
              <el-icon><Clock /></el-icon>
              审核历史
            </el-button>
          </div>
        </div>

        <!-- 审核历史 -->
        <div v-if="reviewHistory.length > 0" class="history-section">
          <h4 class="section-title">
            <el-icon><Histogram /></el-icon>
            审核历史
          </h4>
          <div class="history-list">
            <div v-for="(history, index) in reviewHistory" :key="index" class="history-item">
              <div class="history-header">
                <div class="reviewer">{{ history.reviewerName }}</div>
                <el-tag :type="getHistoryStatusType(history.status)" size="small">
                  {{ getHistoryStatusText(history.status) }}
                </el-tag>
              </div>
              <div class="history-time">{{ formatDate(history.reviewTime) }}</div>
              <div v-if="history.comment" class="history-comment">
                {{ history.comment }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  EditPen, Document, Cpu, Warning, Check,
  CircleCheck, CircleClose, Clock, DocumentAdd,
  Histogram
} from '@element-plus/icons-vue'

const props = defineProps({
  report: {
    type: Object,
    required: true,
    default: () => ({
      reportNo: '',
      status: 'pending',
      content: '',
      aiDiagnosis: '',
      abnormalItems: []
    })
  },
  userInfo: {
    type: Object,
    default: () => ({
      realName: '审核医生',
      role: '主治医师'
    })
  },
  reviewHistory: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['submit', 'save-draft', 'view-history'])

// 审核表单
const reviewForm = ref({
  status: 'approved',
  comment: '',
  signed: false
})

const submitting = ref(false)
const currentTime = ref('')

// 状态映射
const statusMap = {
  pending: { text: '待审核', type: 'info' },
  reviewing: { text: '审核中', type: 'warning' },
  approved: { text: '已通过', type: 'success' },
  rejected: { text: '未通过', type: 'danger' },
  published: { text: '已发布', type: 'primary' }
}

const historyStatusMap = {
  approved: { text: '通过', type: 'success' },
  rejected: { text: '拒绝', type: 'danger' },
  pending: { text: '待修改', type: 'warning' }
}

// 计算属性
const getStatusText = (status) => {
  return statusMap[status]?.text || status
}

const getStatusType = (status) => {
  return statusMap[status]?.type || 'info'
}

const getHistoryStatusText = (status) => {
  return historyStatusMap[status]?.text || status
}

const getHistoryStatusType = (status) => {
  return historyStatusMap[status]?.type || 'info'
}

// 方法
const handleSubmitReview = () => {
  if (!reviewForm.value.signed) {
    ElMessage.warning('请确认电子签名')
    return
  }

  submitting.value = true
  emit('submit', {
    ...reviewForm.value,
    reportId: props.report.id,
    reviewerId: props.userInfo.id,
    reviewerName: props.userInfo.realName
  })

  // 模拟提交
  setTimeout(() => {
    submitting.value = false
    ElMessage.success('审核提交成功')
  }, 1000)
}

const handleSaveDraft = () => {
  emit('save-draft', reviewForm.value)
  ElMessage.info('草稿已保存')
}

const handleViewHistory = () => {
  emit('view-history', props.report.id)
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 初始化当前时间
const updateCurrentTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  updateCurrentTime()
  setInterval(updateCurrentTime, 60000) // 每分钟更新一次
})
</script>

<style scoped>
.report-review-panel {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.report-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.report-no {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.review-content {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 32px;
}

.report-details {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.review-actions {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #303133;
  font-weight: 500;
}

.section-content {
  color: #606266;
  line-height: 1.6;
}

.report-content, .ai-diagnosis {
  padding: 12px;
  background-color: white;
  border-radius: 6px;
  border: 1px solid #ebeef5;
}

.empty-content {
  padding: 12px;
  background-color: #f5f5f5;
  border-radius: 6px;
  color: #909399;
  text-align: center;
  font-style: italic;
}

.abnormal-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.abnormal-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: #fef0f0;
  border-radius: 6px;
  border-left: 4px solid #f56c6c;
}

.item-name {
  font-weight: 500;
  color: #303133;
}

.item-value {
  color: #f56c6c;
  font-weight: bold;
}

.item-range {
  color: #909399;
  font-size: 12px;
}

.action-section {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.review-status {
  margin-bottom: 20px;
}

.status-option {
  display: flex;
  justify-content: center;
}

.review-comment {
  margin-bottom: 20px;
}

.form-item {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #303133;
}

.electronic-signature {
  margin-bottom: 24px;
}

.signature-area {
  background-color: white;
  border-radius: 6px;
  padding: 16px;
  border: 1px solid #ebeef5;
}

.signature-preview {
  text-align: center;
  margin-bottom: 16px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.signature-name {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.signature-role {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.signature-time {
  font-size: 12px;
  color: #909399;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.history-section {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  background-color: white;
  border-radius: 6px;
  padding: 16px;
  border: 1px solid #ebeef5;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.reviewer {
  font-weight: 500;
  color: #303133;
}

.history-time {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.history-comment {
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
  color: #606266;
  font-size: 14px;
  line-height: 1.4;
}
</style>