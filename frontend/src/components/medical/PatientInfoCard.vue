<template>
  <el-card class="patient-info-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <el-icon><User /></el-icon>
        <span>患者信息</span>
      </div>
    </template>

    <!-- 基本信息 -->
    <div class="basic-info">
      <div class="info-item">
        <span class="label">患者姓名：</span>
        <span class="value">{{ patient.name }}</span>
      </div>
      <div class="info-item">
        <span class="label">患者编号：</span>
        <span class="value code">{{ patient.patientNo }}</span>
      </div>
      <div class="info-item">
        <span class="label">性别：</span>
        <span class="value">
          <el-tag :type="patient.gender === '男' ? 'primary' : 'danger'" size="small">
            {{ patient.gender }}
          </el-tag>
        </span>
      </div>
      <div class="info-item">
        <span class="label">年龄：</span>
        <span class="value">{{ patient.age }}岁</span>
      </div>
      <div class="info-item">
        <span class="label">联系电话：</span>
        <span class="value">{{ patient.phone || '未填写' }}</span>
      </div>
    </div>

    <!-- 就诊信息 -->
    <div v-if="patient.visitInfo" class="visit-info">
      <div class="section-title">
        <el-icon><Calendar /></el-icon>
        <span>就诊信息</span>
      </div>
      <div class="info-grid">
        <div class="info-item">
          <span class="label">就诊科室：</span>
          <span class="value">{{ patient.visitInfo.department }}</span>
        </div>
        <div class="info-item">
          <span class="label">就诊医生：</span>
          <span class="value">{{ patient.visitInfo.doctor }}</span>
        </div>
        <div class="info-item">
          <span class="label">就诊时间：</span>
          <span class="value">{{ formatDate(patient.visitInfo.visitTime) }}</span>
        </div>
      </div>
    </div>

    <!-- 过敏史 -->
    <div v-if="patient.allergies && patient.allergies.length > 0" class="allergies">
      <div class="section-title">
        <el-icon><Warning /></el-icon>
        <span>过敏史</span>
      </div>
      <div class="tags">
        <el-tag
          v-for="(allergy, index) in patient.allergies"
          :key="index"
          type="danger"
          size="small"
          class="allergy-tag"
        >
          {{ allergy }}
        </el-tag>
      </div>
    </div>

    <!-- 诊断信息 -->
    <div v-if="patient.diagnosis" class="diagnosis">
      <div class="section-title">
        <el-icon><Document /></el-icon>
        <span>诊断信息</span>
      </div>
      <div class="diagnosis-content">
        {{ patient.diagnosis }}
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button type="primary" size="small" @click="handleViewHistory">
        <el-icon><Clock /></el-icon>
        查看历史
      </el-button>
      <el-button type="info" size="small" @click="handleEdit">
        <el-icon><Edit /></el-icon>
        编辑信息
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
import { User, Calendar, Warning, Document, Clock, Edit } from '@element-plus/icons-vue'

const props = defineProps({
  patient: {
    type: Object,
    required: true,
    default: () => ({
      name: '',
      patientNo: '',
      gender: '男',
      age: 0,
      phone: '',
      visitInfo: null,
      allergies: [],
      diagnosis: ''
    })
  },
  showActions: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['view-history', 'edit'])

const handleViewHistory = () => {
  emit('view-history', props.patient)
}

const handleEdit = () => {
  emit('edit', props.patient)
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}
</script>

<style scoped>
.patient-info-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #303133;
}

.basic-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.info-item {
  display: flex;
  align-items: center;
  min-height: 32px;
}

.label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
}

.value {
  color: #303133;
  font-weight: 500;
}

.value.code {
  font-family: 'Courier New', monospace;
  background-color: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 14px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 16px 0 12px 0;
  font-weight: 500;
  color: #303133;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  padding: 0 16px;
}

.allergies {
  margin-top: 16px;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 0 16px;
}

.allergy-tag {
  margin-bottom: 4px;
}

.diagnosis-content {
  padding: 12px 16px;
  background-color: #fff3e0;
  border-radius: 6px;
  color: #e65100;
  line-height: 1.6;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}
</style>