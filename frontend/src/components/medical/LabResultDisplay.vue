<template>
  <div class="lab-result-display">
    <!-- 结果标题区域 -->
    <div class="result-header">
      <h3 class="result-title">
        <el-icon><Document /></el-icon>
        检验结果
      </h3>
      <div class="result-status">
        <el-tag :type="getStatusType(result.status)" size="small">
          {{ getStatusText(result.status) }}
        </el-tag>
        <el-tag v-if="result.isCritical" type="danger" size="small">
          危急值
        </el-tag>
      </div>
    </div>

    <!-- 患者信息 -->
    <div class="patient-info">
      <div class="info-row">
        <span class="info-label">患者姓名：</span>
        <span class="info-value">{{ result.patientName }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">标本编号：</span>
        <span class="info-value">{{ result.sampleNo }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">送检时间：</span>
        <span class="info-value">{{ formatDate(result.submitTime) }}</span>
      </div>
    </div>

    <!-- 检验项目表格 -->
    <div class="test-items-table">
      <el-table :data="result.testItems" size="small" stripe>
        <el-table-column prop="itemName" label="检验项目" width="180" />
        <el-table-column prop="result" label="检验结果" width="120">
          <template #default="{ row }">
            <span :class="getResultClass(row)">
              {{ row.result }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="referenceRange" label="参考范围" width="150" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getItemStatusType(row.status)" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="提示" width="100">
          <template #default="{ row }">
            <el-icon v-if="row.isAbnormal" color="#f56c6c">
              <Warning />
            </el-icon>
            <el-icon v-if="row.isCritical" color="#e6a23c">
              <Bell />
            </el-icon>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- AI诊断结果 -->
    <div v-if="result.aiDiagnosis" class="ai-diagnosis">
      <div class="ai-header">
        <el-icon><Cpu /></el-icon>
        <span class="ai-title">AI辅助诊断</span>
      </div>
      <div class="ai-content">
        {{ result.aiDiagnosis }}
      </div>
    </div>

    <!-- 审核信息 -->
    <div v-if="result.reviewInfo" class="review-info">
      <div class="review-header">
        <el-icon><EditPen /></el-icon>
        <span class="review-title">审核信息</span>
      </div>
      <div class="review-content">
        <div class="review-row">
          <span class="review-label">审核人：</span>
          <span class="review-value">{{ result.reviewInfo.reviewerName }}</span>
        </div>
        <div class="review-row">
          <span class="review-label">审核时间：</span>
          <span class="review-value">{{ formatDate(result.reviewInfo.reviewTime) }}</span>
        </div>
        <div v-if="result.reviewInfo.remark" class="review-row">
          <span class="review-label">审核意见：</span>
          <span class="review-value">{{ result.reviewInfo.remark }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Document, Warning, Bell, Cpu, EditPen } from '@element-plus/icons-vue'

const props = defineProps({
  result: {
    type: Object,
    required: true,
    default: () => ({
      status: 'completed',
      isCritical: false,
      patientName: '',
      sampleNo: '',
      submitTime: '',
      testItems: [],
      aiDiagnosis: '',
      reviewInfo: null
    })
  }
})

// 状态映射
const statusMap = {
  pending: { text: '待审核', type: 'info' },
  reviewing: { text: '审核中', type: 'warning' },
  completed: { text: '已完成', type: 'success' },
  abnormal: { text: '异常', type: 'danger' }
}

// 方法
const getStatusText = (status) => {
  return statusMap[status]?.text || status
}

const getStatusType = (status) => {
  return statusMap[status]?.type || 'info'
}

const getItemStatusType = (status) => {
  const map = {
    '正常': 'success',
    '偏高': 'warning',
    '偏低': 'warning',
    '异常': 'danger',
    '危急': 'danger'
  }
  return map[status] || 'info'
}

const getResultClass = (row) => {
  if (row.isCritical) return 'critical-result'
  if (row.isAbnormal) return 'abnormal-result'
  return 'normal-result'
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
</script>

<style scoped>
.lab-result-display {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.result-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.result-status {
  display: flex;
  gap: 8px;
}

.patient-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.info-row {
  display: flex;
  align-items: center;
}

.info-label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
}

.info-value {
  color: #303133;
  font-weight: 500;
}

.test-items-table {
  margin-bottom: 20px;
}

.critical-result {
  color: #f56c6c;
  font-weight: bold;
}

.abnormal-result {
  color: #e6a23c;
  font-weight: bold;
}

.normal-result {
  color: #67c23a;
}

.ai-diagnosis, .review-info {
  margin-top: 20px;
  padding: 16px;
  background-color: #f0f9ff;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.ai-header, .review-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-weight: 500;
  color: #303133;
}

.ai-content, .review-content {
  color: #606266;
  line-height: 1.6;
}

.review-row {
  display: flex;
  margin-bottom: 8px;
}

.review-label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
}

.review-value {
  color: #303133;
}
</style>