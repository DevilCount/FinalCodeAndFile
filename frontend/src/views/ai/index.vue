<template>
  <div class="ai-container">
    <h2 class="page-title">AI诊断</h2>
    
    <el-card shadow="hover" class="ai-card">
      <template #header>
        <div class="card-header">
          <span>AI辅助诊断</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="血常规诊断" name="blood">
          <el-form
            ref="bloodFormRef"
            :model="bloodForm"
            :rules="bloodRules"
            label-width="120px"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="白细胞" prop="whiteBloodCell">
                  <el-input
                    v-model.number="bloodForm.whiteBloodCell"
                    placeholder="请输入白细胞值 (× 10^9/L)"
                    type="number"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="红细胞" prop="redBloodCell">
                  <el-input
                    v-model.number="bloodForm.redBloodCell"
                    placeholder="请输入红细胞值 (× 10^12/L)"
                    type="number"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="血红蛋白" prop="hemoglobin">
                  <el-input
                    v-model.number="bloodForm.hemoglobin"
                    placeholder="请输入血红蛋白值 (g/L)"
                    type="number"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="血小板" prop="platelet">
                  <el-input
                    v-model.number="bloodForm.platelet"
                    placeholder="请输入血小板值 (× 10^9/L)"
                    type="number"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item>
              <el-button type="primary" @click="handleBloodDiagnose">
                <el-icon><Cpu /></el-icon>
                开始诊断
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="尿常规诊断" name="urine">
          <el-form
            ref="urineFormRef"
            :model="urineForm"
            :rules="urineRules"
            label-width="120px"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="尿蛋白" prop="protein">
                  <el-select
                    v-model="urineForm.protein"
                    placeholder="请选择尿蛋白结果"
                    style="width: 100%"
                  >
                    <el-option label="阴性" value="negative" />
                    <el-option label="弱阳性" value="weakly_positive" />
                    <el-option label="阳性" value="positive" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="尿糖" prop="glucose">
                  <el-select
                    v-model="urineForm.glucose"
                    placeholder="请选择尿糖结果"
                    style="width: 100%"
                  >
                    <el-option label="阴性" value="negative" />
                    <el-option label="弱阳性" value="weakly_positive" />
                    <el-option label="阳性" value="positive" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="红细胞" prop="redBloodCell">
                  <el-input
                    v-model.number="urineForm.redBloodCell"
                    placeholder="请输入红细胞数量"
                    type="number"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="白细胞" prop="whiteBloodCell">
                  <el-input
                    v-model.number="urineForm.whiteBloodCell"
                    placeholder="请输入白细胞数量"
                    type="number"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item>
              <el-button type="primary" @click="handleUrineDiagnose">
                <el-icon><Cpu /></el-icon>
                开始诊断
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <!-- 诊断结果 -->
    <el-card shadow="hover" class="result-card" v-if="diagnosisResult">
      <template #header>
        <div class="card-header">
          <span>诊断结果</span>
        </div>
      </template>
      
      <div class="result-content">
        <h3>{{ diagnosisResult.title }}</h3>
        <div class="result-body">
          {{ diagnosisResult.content }}
        </div>
        <div class="result-suggestion" v-if="diagnosisResult.suggestion">
          <h4>建议：</h4>
          <p>{{ diagnosisResult.suggestion }}</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Cpu } from '@element-plus/icons-vue'
import aiService from '../../services/aiService'

// 标签页
const activeTab = ref('blood')

// 血常规表单
const bloodFormRef = ref(null)
const bloodForm = ref({
  whiteBloodCell: '',
  redBloodCell: '',
  hemoglobin: '',
  platelet: ''
})
const bloodRules = {
  whiteBloodCell: [
    { required: true, message: '请输入白细胞值', trigger: 'blur' }
  ],
  redBloodCell: [
    { required: true, message: '请输入红细胞值', trigger: 'blur' }
  ],
  hemoglobin: [
    { required: true, message: '请输入血红蛋白值', trigger: 'blur' }
  ],
  platelet: [
    { required: true, message: '请输入血小板值', trigger: 'blur' }
  ]
}

// 尿常规表单
const urineFormRef = ref(null)
const urineForm = ref({
  protein: '',
  glucose: '',
  redBloodCell: '',
  whiteBloodCell: ''
})
const urineRules = {
  protein: [
    { required: true, message: '请选择尿蛋白结果', trigger: 'change' }
  ],
  glucose: [
    { required: true, message: '请选择尿糖结果', trigger: 'change' }
  ],
  redBloodCell: [
    { required: true, message: '请输入红细胞数量', trigger: 'blur' }
  ],
  whiteBloodCell: [
    { required: true, message: '请输入白细胞数量', trigger: 'blur' }
  ]
}

// 诊断结果
const diagnosisResult = ref(null)

// 方法
const handleBloodDiagnose = async () => {
  if (!bloodFormRef.value) return
  await bloodFormRef.value.validate(async (valid, fields) => {
    if (valid) {
      try {
        const response = await aiService.diagnoseBloodRoutine(bloodForm.value)
        if (response.code === 200) {
          diagnosisResult.value = {
            title: '血常规诊断结果',
            content: response.data.diagnosis || response.data.result || '诊断完成',
            suggestion: Array.isArray(response.data.suggestions)
              ? response.data.suggestions.join('；')
              : (response.data.details?.recommendations?.join('；') || '请咨询专业医生')
          }
        } else {
          ElMessage.error(response.message || '诊断失败')
        }
      } catch (error) {
        ElMessage.error('诊断失败，请检查网络连接')
        console.error('血常规诊断错误:', error)
      }
    } else {
      console.log('表单验证失败:', fields)
    }
  })
}

const handleUrineDiagnose = async () => {
  if (!urineFormRef.value) return
  await urineFormRef.value.validate(async (valid, fields) => {
    if (valid) {
      try {
        const response = await aiService.diagnoseUrineRoutine(urineForm.value)
        if (response.code === 200) {
          diagnosisResult.value = {
            title: '尿常规诊断结果',
            content: response.data.diagnosis || response.data.result || '诊断完成',
            suggestion: Array.isArray(response.data.suggestions)
              ? response.data.suggestions.join('；')
              : (response.data.details?.recommendations?.join('；') || '请咨询专业医生')
          }
        } else {
          ElMessage.error(response.message || '诊断失败')
        }
      } catch (error) {
        ElMessage.error('诊断失败，请检查网络连接')
        console.error('尿常规诊断错误:', error)
      }
    } else {
      console.log('表单验证失败:', fields)
    }
  })
}
</script>

<style lang="scss" scoped>
.ai-container {
  padding: 0;
  background: transparent;
  min-height: 100%;
  
  .ai-card,
  .result-card {
    border-radius: var(--border-radius-xl) !important;
    border: 1px solid var(--border-light) !important;
    box-shadow: var(--shadow-sm) !important;
    
    :deep(.el-card__header) {
      padding: var(--spacing-lg) var(--spacing-xl);
      border-bottom: 1px solid var(--border-light);
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%);
    }
    
    :deep(.el-card__body) {
      padding: var(--spacing-xl);
    }
  }
  
  .card-header {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    
    .el-icon {
      color: var(--medical-purple);
    }
  }
  
  .result-content {
    h3 {
      margin: 0 0 var(--spacing-md) 0;
      color: var(--text-primary);
      font-size: var(--font-size-xl);
      font-weight: var(--font-weight-bold);
    }
    
    .result-body {
      margin-bottom: var(--spacing-lg);
      line-height: 1.8;
      color: var(--text-secondary);
      font-size: var(--font-size-md);
      padding: var(--spacing-lg);
      background: linear-gradient(135deg, var(--primary-bg) 0%, #e1f5fe 100%);
      border-radius: var(--border-radius-lg);
      border-left: 4px solid var(--primary-color);
    }
    
    .result-suggestion {
      h4 {
        margin: 0 0 var(--spacing-sm) 0;
        color: var(--text-primary);
        font-size: var(--font-size-lg);
        font-weight: var(--font-weight-semibold);
      }
      
      p {
        margin: 0;
        line-height: 1.8;
        color: var(--text-secondary);
        font-size: var(--font-size-md);
        padding: var(--spacing-md) var(--spacing-lg);
        background: var(--success-bg);
        border-radius: var(--border-radius-md);
        border-left: 4px solid var(--success-color);
      }
    }
  }
}
</style>
