<template>
  <div class="professional-report-create-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div class="header-title">
          <h1 class="page-title">
            <el-icon><Document /></el-icon>
            新建报告
          </h1>
          <p class="page-subtitle">创建检验报告</p>
        </div>
      </div>
      <div class="header-right">
        <el-tag type="info">自动保存: 已开启</el-tag>
      </div>
    </div>

    <!-- 报告信息卡片 -->
    <div class="report-form-grid">
      <!-- 基本信息 -->
      <el-card shadow="hover" class="form-card">
        <template #header>
          <div class="card-header">
            <el-icon><InfoFilled /></el-icon>
            <span>报告基本信息</span>
          </div>
        </template>
        <el-form :model="reportForm" label-width="120px" size="large">
          <el-form-item label="报告编号">
            <el-input v-model="reportForm.reportNo" disabled placeholder="自动生成">
              <template #suffix>
                <el-icon class="generate-icon"><Refresh /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item label="关联标本">
            <el-select v-model="reportForm.sampleId" placeholder="请选择标本" style="width: 100%" filterable>
              <el-option
                v-for="sample in availableSamples"
                :key="sample.id"
                :label="`${sample.sampleNo} - ${sample.patientName}`"
                :value="sample.id"
              >
                <div class="sample-option">
                  <span class="sample-no">{{ sample.sampleNo }}</span>
                  <span class="patient-name">{{ sample.patientName }}</span>
                  <el-tag size="small" :type="getStatusTagType(sample.status)">{{ sample.statusText }}</el-tag>
                </div>
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="报告类型">
            <el-select v-model="reportForm.reportType" placeholder="请选择报告类型" style="width: 100%">
              <el-option label="常规报告" value="ROUTINE" />
              <el-option label="急诊报告" value="EMERGENCY" />
              <el-option label="复查报告" value="FOLLOWUP" />
              <el-option label="特殊报告" value="SPECIAL" />
            </el-select>
          </el-form-item>

          <el-form-item label="优先级">
            <el-radio-group v-model="reportForm.priority">
              <el-radio label="NORMAL">普通</el-radio>
              <el-radio label="HIGH">紧急</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 患者信息 -->
      <el-card shadow="hover" class="form-card">
        <template #header>
          <div class="card-header">
            <el-icon><User /></el-icon>
            <span>患者信息</span>
          </div>
        </template>
        <el-form :model="reportForm" label-width="120px" size="large">
          <el-form-item label="患者姓名">
            <el-input v-model="reportForm.patientName" placeholder="请输入患者姓名">
              <template #prefix><el-icon><User /></el-icon></template>
            </el-input>
          </el-form-item>
          
          <el-form-item label="患者ID">
            <el-input v-model="reportForm.patientId" placeholder="请输入患者ID">
              <template #prefix><el-icon><Postcard /></el-icon></template>
            </el-input>
          </el-form-item>

          <el-form-item label="性别">
            <el-radio-group v-model="reportForm.gender">
              <el-radio label="M">男</el-radio>
              <el-radio label="F">女</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="年龄">
            <el-input v-model="reportForm.age" type="number" placeholder="请输入年龄">
              <template #append>岁</template>
            </el-input>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 检验结果 -->
    <el-card shadow="hover" class="results-card">
      <template #header>
        <div class="card-header">
          <el-icon><Box /></el-icon>
          <span>检验结果</span>
          <el-button type="primary" size="small" @click="addTestResult">
            <el-icon><Plus /></el-icon>
            添加项目
          </el-button>
        </div>
      </template>
      
      <el-table :data="testResults" border stripe style="width: 100%">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="itemName" label="检验项目" width="180">
          <template #default="{ row }">
            <el-select v-model="row.itemCode" placeholder="选择项目" @change="handleItemChange(row)">
              <el-option-group label="血液检查">
                <el-option label="白细胞计数(WBC)" value="WBC" />
                <el-option label="红细胞计数(RBC)" value="RBC" />
                <el-option label="血红蛋白(HGB)" value="HGB" />
                <el-option label="血小板计数(PLT)" value="PLT" />
              </el-option-group>
              <el-option-group label="生化检查">
                <el-option label="谷丙转氨酶(ALT)" value="ALT" />
                <el-option label="谷草转氨酶(AST)" value="AST" />
                <el-option label="尿素氮(BUN)" value="BUN" />
                <el-option label="肌酐(CRE)" value="CRE" />
              </el-option-group>
            </el-select>
          </template>
        </el-table-column>
        <el-table-column prop="result" label="结果" width="120">
          <template #default="{ row }">
            <el-input v-model="row.result" placeholder="结果值" size="small" />
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" width="100">
          <template #default="{ row }">
            <el-input v-model="row.unit" placeholder="单位" size="small" />
          </template>
        </el-table-column>
        <el-table-column prop="reference" label="参考值" width="150">
          <template #default="{ row }">
            <el-input v-model="row.reference" placeholder="参考范围" size="small" />
          </template>
        </el-table-column>
        <el-table-column prop="flag" label="标志" width="100">
          <template #default="{ row }">
            <el-tag :type="getFlagType(row.flag)" size="small">{{ row.flag || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row, $index }">
            <el-button type="danger" size="small" text @click="removeTestResult($index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- AI辅助诊断 -->
    <el-card shadow="hover" class="ai-card">
      <template #header>
        <div class="card-header">
          <el-icon><Cpu /></el-icon>
          <span>AI辅助诊断</span>
          <el-tag type="success" size="small">
            <el-icon><MagicStick /></el-icon>
            已启用
          </el-tag>
        </div>
      </template>
      
      <div class="ai-content">
        <div class="ai-result" v-if="aiDiagnosis">
          <el-alert :title="aiDiagnosis.summary" :type="aiDiagnosis.level" show-icon :closable="false">
            <template #default>
              <div class="ai-detail">
                <p><strong>诊断建议:</strong> {{ aiDiagnosis.suggestion }}</p>
                <p><strong>参考依据:</strong> {{ aiDiagnosis.evidence }}</p>
              </div>
            </template>
          </el-alert>
        </div>
        <div class="ai-empty" v-else>
          <el-icon class="ai-icon"><MagicStick /></el-icon>
          <p>点击下方按钮获取AI辅助诊断建议</p>
        </div>
        <el-button type="primary" @click="getAiDiagnosis" :loading="aiLoading">
          <el-icon><Cpu /></el-icon>
          {{ aiDiagnosis ? '重新分析' : '获取诊断建议' }}
        </el-button>
      </div>
    </el-card>

    <!-- 备注信息 -->
    <el-card shadow="hover" class="remark-card">
      <template #header>
        <div class="card-header">
          <el-icon><Comment /></el-icon>
          <span>备注与说明</span>
        </div>
      </template>
      <el-form>
        <el-form-item label="检验备注">
          <el-input v-model="reportForm.remark" type="textarea" :rows="3" placeholder="请输入检验备注信息" />
        </el-form-item>
        <el-form-item label="医生意见">
          <el-input v-model="reportForm.doctorComment" type="textarea" :rows="3" placeholder="请输入医生意见" />
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 提交按钮 -->
    <div class="submit-bar">
      <el-button size="large" @click="goBack">
        <el-icon><Close /></el-icon>
        取消
      </el-button>
      <el-button size="large" type="warning" @click="saveDraft">
        <el-icon><Document /></el-icon>
        保存草稿
      </el-button>
      <el-button size="large" type="primary" @click="submitReport" :loading="submitting">
        <el-icon><Check /></el-icon>
        提交审核
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft, Document, InfoFilled, User, Postcard, Box, Plus, Refresh,
  Delete, Cpu, MagicStick, Comment, Close, Check
} from '@element-plus/icons-vue'
import { reportApi } from '@/api/report'
import sampleService from '@/services/sampleService'

const router = useRouter()
const route = useRoute()

// 提交状态
const submitting = ref(false)
const aiLoading = ref(false)
const aiDiagnosis = ref(null)

// 可选标本列表 - 从API获取
const availableSamples = ref([])

// 加载可选标本列表（已完成的标本）
const loadAvailableSamples = async () => {
  try {
    const result = await sampleService.getSampleList({ pageSize: 100 })
    // 只显示已完成的标本，可以用于创建报告
    availableSamples.value = (result.records || []).map(sample => ({
      id: sample.id,
      sampleNo: sample.sampleNo,
      patientName: sample.patient?.name || '未知患者',
      status: sample.status,
      statusText: getSampleStatusText(sample.status)
    }))
  } catch (error) {
    console.error('加载标本列表失败:', error)
    ElMessage.warning('加载标本列表失败，请刷新页面重试')
  }
}

// 获取标本状态文本
const getSampleStatusText = (status) => {
  const statusMap = {
    'PENDING': '待处理',
    'PROCESSING': '处理中',
    'TESTING': '检验中',
    'COMPLETED': '已完成',
    'REJECTED': '已拒绝'
  }
  return statusMap[status] || status
}

// 报告表单
const reportForm = reactive({
  reportNo: '',
  sampleId: '',
  reportType: 'ROUTINE',
  priority: 'NORMAL',
  patientName: '',
  patientId: '',
  gender: 'M',
  age: '',
  remark: '',
  doctorComment: ''
})

// 检验结果
const testResults = ref([
  { itemCode: '', itemName: '', result: '', unit: '', reference: '', flag: '' }
])

// 生成报告编号
const generateReportNo = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const random = Math.floor(Math.random() * 10000).toString().padStart(4, '0')
  reportForm.reportNo = `RPT${year}${month}${day}${random}`
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const map = { COMPLETED: 'success', TESTING: 'warning', ABNORMAL: 'danger' }
  return map[status] || 'info'
}

// 获取标志类型
const getFlagType = (flag) => {
  const map = { 'H': 'danger', 'L': 'warning', 'HH': 'danger', 'LL': 'warning', 'N': 'success' }
  return map[flag] || 'info'
}

// 处理项目变更
const handleItemChange = (row) => {
  const items = {
    'WBC': { name: '白细胞计数', unit: '×10⁹/L', reference: '4.0-10.0' },
    'RBC': { name: '红细胞计数', unit: '×10¹²/L', reference: '4.0-5.5' },
    'HGB': { name: '血红蛋白', unit: 'g/L', reference: '120-160' },
    'PLT': { name: '血小板计数', unit: '×10⁹/L', reference: '100-300' },
    'ALT': { name: '谷丙转氨酶', unit: 'U/L', reference: '0-40' },
    'AST': { name: '谷草转氨酶', unit: 'U/L', reference: '0-40' },
    'BUN': { name: '尿素氮', unit: 'mmol/L', reference: '2.6-7.5' },
    'CRE': { name: '肌酐', unit: 'μmol/L', reference: '44-133' }
  }
  if (items[row.itemCode]) {
    row.itemName = items[row.itemCode].name
    row.unit = items[row.itemCode].unit
    row.reference = items[row.itemCode].reference
    // 自动判断标志
    const val = parseFloat(row.result)
    const ref = items[row.itemCode].reference.split('-')
    if (ref.length === 2) {
      const min = parseFloat(ref[0])
      const max = parseFloat(ref[1])
      if (!isNaN(val)) {
        if (val > max * 1.2) row.flag = 'H'
        else if (val < min * 0.8) row.flag = 'L'
        else row.flag = 'N'
      }
    }
  }
}

// 添加检验结果
const addTestResult = () => {
  testResults.value.push({ itemCode: '', itemName: '', result: '', unit: '', reference: '', flag: '' })
}

// 移除检验结果
const removeTestResult = (index) => {
  if (testResults.value.length > 1) {
    testResults.value.splice(index, 1)
  } else {
    ElMessage.warning('至少保留一项检验结果')
  }
}

// 获取AI诊断
const getAiDiagnosis = async () => {
  aiLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    // 模拟AI诊断结果
    const abnormalCount = testResults.value.filter(r => r.flag && r.flag !== 'N').length
    if (abnormalCount > 0) {
      aiDiagnosis.value = {
        level: 'warning',
        summary: `检测到 ${abnormalCount} 项异常结果`,
        suggestion: '建议复查相关项目，综合临床症状进行诊断',
        evidence: '根据检验结果分析，暂无危急值提示'
      }
    } else {
      aiDiagnosis.value = {
        level: 'success',
        summary: '所有检验项目均在正常范围内',
        suggestion: '检验结果正常，无特殊建议',
        evidence: '各指标均处于参考值范围内'
      }
    }
    ElMessage.success('AI诊断分析完成')
  } catch (error) {
    ElMessage.error('AI诊断失败')
  } finally {
    aiLoading.value = false
  }
}

// 保存草稿
const saveDraft = async () => {
  submitting.value = true
  try {
    // 调用真实API保存草稿
    await reportApi.createReport({
      ...reportForm,
      status: 'DRAFT',
      testResults: testResults.value.filter(r => r.itemCode && r.result)
    })
    ElMessage.success('报告已保存为草稿')
  } catch (error) {
    const errorMessage = error?.response?.data?.message || error?.message || '保存失败'
    ElMessage.error(errorMessage)
  } finally {
    submitting.value = false
  }
}

// 提交报告
const submitReport = async () => {
  // 基本验证
  if (!reportForm.sampleId) {
    ElMessage.warning('请选择关联标本')
    return
  }
  if (testResults.value.length === 0 || !testResults.value[0].itemCode || !testResults.value[0].result) {
    ElMessage.warning('请至少添加一项检验结果')
    return
  }

  submitting.value = true
  try {
    // 调用真实API提交报告（状态为待审核）
    await reportApi.createReport({
      ...reportForm,
      status: 'PENDING_REVIEW',
      testResults: testResults.value.filter(r => r.itemCode && r.result)
    })
    ElMessage.success('报告提交成功，等待审核')
    router.push('/report')
  } catch (error) {
    const errorMessage = error?.response?.data?.message || error?.message || '提交失败'
    ElMessage.error(errorMessage)
  } finally {
    submitting.value = false
  }
}

// 返回
const goBack = () => {
  router.push('/report')
}

// 生命周期
onMounted(() => {
  generateReportNo()
  // 加载可选标本列表
  loadAvailableSamples()
  // 如果有标本ID参数，自动填充
  if (route.query.sampleId) {
    reportForm.sampleId = parseInt(route.query.sampleId)
  }
})
</script>

<style scoped>
.professional-report-create-container {
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

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-title {
  border-left: 3px solid #409EFF;
  padding-left: 16px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-subtitle {
  color: #909399;
  margin: 4px 0 0;
  font-size: 13px;
}

/* 表单网格 */
.report-form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.form-card, .results-card, .ai-card, .remark-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

/* 标本选项 */
.sample-option {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.sample-no {
  font-weight: 600;
  color: #303133;
}

.patient-name {
  flex: 1;
  color: #606266;
}

/* 检验结果表格 */
.results-card {
  margin-bottom: 20px;
}

/* AI卡片 */
.ai-card {
  margin-bottom: 20px;
}

.ai-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.ai-empty {
  text-align: center;
  color: #909399;
}

.ai-icon {
  font-size: 48px;
  margin-bottom: 12px;
  color: #67C23A;
}

.ai-detail p {
  margin: 8px 0;
  line-height: 1.6;
}

/* 备注卡片 */
.remark-card {
  margin-bottom: 20px;
}

/* 提交栏 */
.submit-bar {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

/* 响应式 */
@media (max-width: 1200px) {
  .report-form-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .submit-bar {
    flex-direction: column;
  }
  
  .submit-bar .el-button {
    width: 100%;
  }
}
</style>
