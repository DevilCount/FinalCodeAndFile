<template>
  <div class="professional-create-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div class="header-title">
          <h1 class="page-title">
            <el-icon><Plus /></el-icon>
            新建标本
          </h1>
          <p class="page-subtitle">创建新的检验标本</p>
        </div>
      </div>
    </div>

    <!-- 快速操作提示 -->
    <el-alert
      title="填写提示"
      type="info"
      :closable="false"
      show-icon
      class="tip-alert"
    >
      <template #default>
        请完整填写以下信息创建新标本。<strong>标注*</strong>的字段为必填项。
      </template>
    </el-alert>

    <!-- 表单区域 -->
    <div class="form-container">
      <el-card shadow="hover" class="form-card">
        <el-form
          ref="sampleFormRef"
          :model="sampleForm"
          :rules="sampleRules"
          label-width="140px"
          size="large"
        >
          <!-- 基本信息 -->
          <div class="form-section">
            <div class="section-header">
              <el-icon><InfoFilled /></el-icon>
              <span>基本信息</span>
            </div>
            
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="标本编号" prop="sampleNo">
                  <el-input v-model="sampleForm.sampleNo" disabled placeholder="自动生成">
                    <template #suffix>
                      <el-icon class="generate-icon" @click="generateSampleNo">
                        <Refresh />
                      </el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="标本类型" prop="sampleType">
                  <el-select v-model="sampleForm.sampleType" placeholder="请选择标本类型" style="width: 100%">
                    <el-option label="🩸 血液" value="blood" />
                    <el-option label="🧪 尿液" value="urine" />
                    <el-option label="🦠 分泌物" value="secretion" />
                    <el-option label="🔬 组织" value="tissue" />
                    <el-option label="💧 胸水" value="pleural" />
                    <el-option label="💧 腹水" value="ascites" />
                    <el-option label="🧠 脑脊液" value="csf" />
                    <el-option label="💩 粪便" value="feces" />
                    <el-option label="📦 其他" value="other" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="8">
                <el-form-item label="优先级" prop="priority">
                  <el-radio-group v-model="sampleForm.priority">
                    <el-radio label="NORMAL">普通</el-radio>
                    <el-radio label="HIGH">紧急</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="采集时间" prop="collectTime">
                  <el-date-picker
                    v-model="sampleForm.collectTime"
                    type="datetime"
                    placeholder="选择采集时间"
                    style="width: 100%"
                    format="YYYY-MM-DD HH:mm"
                    value-format="YYYY-MM-DD HH:mm:ss"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <!-- 患者信息 -->
          <div class="form-section">
            <div class="section-header">
              <el-icon><User /></el-icon>
              <span>患者信息</span>
              <el-tag type="warning" size="small">必填</el-tag>
            </div>
            
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="患者姓名" prop="patientName">
                  <el-input v-model="sampleForm.patientName" placeholder="请输入患者姓名">
                    <template #prefix>
                      <el-icon><User /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="患者ID" prop="patientId">
                  <el-input v-model="sampleForm.patientId" placeholder="请输入患者ID">
                    <template #prefix>
                      <el-icon><Postcard /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="8">
                <el-form-item label="性别" prop="gender">
                  <el-radio-group v-model="sampleForm.gender">
                    <el-radio label="M">男</el-radio>
                    <el-radio label="F">女</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="年龄" prop="age">
                  <el-input v-model="sampleForm.age" placeholder="请输入年龄" type="number">
                    <template #append>岁</template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="联系电话" prop="phone">
                  <el-input v-model="sampleForm.phone" placeholder="请输入联系电话">
                    <template #prefix>
                      <el-icon><Phone /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <!-- 送检信息 -->
          <div class="form-section">
            <div class="section-header">
              <el-icon><OfficeBuilding /></el-icon>
              <span>送检信息</span>
            </div>
            
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="送检科室" prop="department">
                  <el-select v-model="sampleForm.department" placeholder="请选择或输入科室" style="width: 100%" filterable allow-create>
                    <el-option label="内科" value="内科" />
                    <el-option label="外科" value="外科" />
                    <el-option label="儿科" value="儿科" />
                    <el-option label="妇产科" value="妇产科" />
                    <el-option label="急诊科" value="急诊科" />
                    <el-option label="体检科" value="体检科" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="送检医生" prop="doctor">
                  <el-input v-model="sampleForm.doctor" placeholder="请输入送检医生姓名">
                    <template #prefix>
                      <el-icon><User /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="24">
                <el-form-item label="临床诊断" prop="diagnosis">
                  <el-input v-model="sampleForm.diagnosis" type="textarea" :rows="2" placeholder="请输入临床诊断信息" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <!-- 检验项目 -->
          <div class="form-section">
            <div class="section-header">
              <el-icon><Box /></el-icon>
              <span>检验项目</span>
              <el-tag type="warning" size="small">必填</el-tag>
            </div>
            
            <el-row :gutter="24">
              <el-col :span="24">
                <el-form-item label="选择检验项目" prop="testItems">
                  <el-checkbox-group v-model="selectedTestCategories">
                    <el-checkbox-button
                      v-for="category in testCategories"
                      :key="category.name"
                      :label="category.name"
                    >
                      {{ category.label }}
                    </el-checkbox-button>
                  </el-checkbox-group>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="24">
                <el-form-item label="详细项目" prop="testItemDetails">
                  <el-select
                    v-model="sampleForm.testItems"
                    placeholder="请选择检验项目"
                    multiple
                    filterable
                    style="width: 100%"
                  >
                    <el-option-group
                      v-for="category in filteredTestItems"
                      :key="category.label"
                      :label="category.label"
                    >
                      <el-option
                        v-for="item in category.items"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                      >
                        <span style="float: left">{{ item.label }}</span>
                        <span style="float: right; color: #8492a6; font-size: 13px">{{ item.code }}</span>
                      </el-option>
                    </el-option-group>
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="24">
                <div class="selected-items-preview" v-if="sampleForm.testItems.length > 0">
                  <span class="preview-label">已选项目:</span>
                  <el-tag
                    v-for="item in sampleForm.testItems"
                    :key="item"
                    closable
                    @close="removeTestItem(item)"
                    style="margin-right: 8px; margin-bottom: 4px;"
                  >
                    {{ getTestItemName(item) }}
                  </el-tag>
                </div>
              </el-col>
            </el-row>
          </div>

          <!-- 备注信息 -->
          <div class="form-section">
            <div class="section-header">
              <el-icon><Comment /></el-icon>
              <span>备注信息</span>
            </div>
            
            <el-row :gutter="24">
              <el-col :span="24">
                <el-form-item label="备注">
                  <el-input v-model="sampleForm.remark" type="textarea" :rows="3" placeholder="请输入备注信息（可选）" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <!-- 提交按钮 -->
          <div class="form-actions">
            <el-button @click="goBack" size="large">
              <el-icon><Close /></el-icon>
              取消
            </el-button>
            <el-button type="primary" size="large" @click="handleSubmit" :loading="submitting">
              <el-icon><Check /></el-icon>
              提交创建
            </el-button>
            <el-button type="success" size="large" @click="handleSubmitAndContinue" :loading="submitting">
              <el-icon><Plus /></el-icon>
              提交并继续
            </el-button>
          </div>
        </el-form>
      </el-card>
    </div>

    <!-- 快捷模板 -->
    <el-card shadow="hover" class="template-card">
      <template #header>
        <div class="card-header">
          <el-icon><MagicStick /></el-icon>
          <span>快捷模板</span>
        </div>
      </template>
      <div class="template-list">
        <el-tag
          v-for="template in quickTemplates"
          :key="template.name"
          class="template-tag"
          @click="applyTemplate(template)"
        >
          {{ template.name }}
        </el-tag>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft, Plus, InfoFilled, User, Postcard, Phone, OfficeBuilding,
  UserFilled, Box, Comment, Refresh, Close, Check, MagicStick
} from '@element-plus/icons-vue'
import sampleService from '@/services/sampleService'

const router = useRouter()

// 表单引用
const sampleFormRef = ref(null)

// 提交状态
const submitting = ref(false)

// 选中的检验类别
const selectedTestCategories = ref([])

// 检验类别
const testCategories = [
  {
    name: 'blood',
    label: '🩸 血液检查',
    items: [
      { value: 'CBC', label: '血常规检查', code: 'CBC' },
      { value: 'BPC', label: '血小板计数', code: 'BPC' },
      { value: 'RET', label: '网织红细胞计数', code: 'RET' },
      { value: 'ESR', label: '红细胞沉降率', code: 'ESR' }
    ]
  },
  {
    name: 'biochemistry',
    label: '🧪 生化检查',
    items: [
      { value: 'LFT', label: '肝功能检测', code: 'LFT' },
      { value: 'RFT', label: '肾功能检测', code: 'RFT' },
      { value: 'GLU', label: '血糖测定', code: 'GLU' },
      { value: 'LIP', label: '血脂分析', code: 'LIP' }
    ]
  },
  {
    name: 'immune',
    label: '💉 免疫检查',
    items: [
      { value: 'TFT', label: '甲状腺功能', code: 'TFT' },
      { value: 'TUMOR', label: '肿瘤标志物', code: 'TUMOR' },
      { value: 'AUTO', label: '自身抗体', code: 'AUTO' }
    ]
  },
  {
    name: 'urinary',
    label: '🧪 尿液检查',
    items: [
      { value: 'URT', label: '尿常规检查', code: 'URT' },
      { value: 'UPRO', label: '尿蛋白定量', code: 'UPRO' },
      { value: 'UBLD', label: '尿潜血', code: 'UBLD' }
    ]
  }
]

// 过滤后的检验项目
const filteredTestItems = computed(() => {
  if (selectedTestCategories.value.length === 0) {
    return testCategories
  }
  return testCategories.filter(cat => selectedTestCategories.value.includes(cat.name))
})

// 快捷模板
const quickTemplates = [
  { name: '常规体检', testItems: ['CBC', 'LFT', 'RFT', 'GLU', 'URT'], department: '体检科' },
  { name: '住院常规', testItems: ['CBC', 'LFT', 'RFT', 'LIP'], department: '内科' },
  { name: '术前检查', testItems: ['CBC', 'LFT', 'RFT', 'GLU', 'LIP', 'URT'], department: '外科' },
  { name: '发热检查', testItems: ['CBC', 'ESR', 'CRP'], department: '内科' }
]

// 表单数据
const sampleForm = reactive({
  sampleNo: '',
  sampleType: '',
  priority: 'NORMAL',
  collectTime: '',
  patientName: '',
  patientId: '',
  gender: 'M',
  age: '',
  phone: '',
  department: '',
  doctor: '',
  diagnosis: '',
  testItems: [],
  remark: ''
})

// 表单验证规则
const sampleRules = {
  sampleType: [
    { required: true, message: '请选择标本类型', trigger: 'change' }
  ],
  patientName: [
    { required: true, message: '请输入患者姓名', trigger: 'blur' }
  ],
  patientId: [
    { required: true, message: '请输入患者ID', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  age: [
    { required: true, message: '请输入年龄', trigger: 'blur' }
  ],
  department: [
    { required: true, message: '请选择或输入科室', trigger: 'change' }
  ],
  doctor: [
    { required: true, message: '请输入送检医生', trigger: 'blur' }
  ],
  testItems: [
    { type: 'array', required: true, message: '请选择至少一个检验项目', trigger: 'change' }
  ]
}

// 生成标本编号
const generateSampleNo = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0')
  sampleForm.sampleNo = `S${year}${month}${day}${hours}${minutes}${random}`
}

// 获取检验项目名称
const getTestItemName = (code) => {
  for (const category of testCategories) {
    const item = category.items.find(i => i.value === code)
    if (item) return item.label
  }
  return code
}

// 移除检验项目
const removeTestItem = (item) => {
  sampleForm.testItems = sampleForm.testItems.filter(i => i !== item)
}

// 应用模板
const applyTemplate = (template) => {
  sampleForm.testItems = [...template.testItems]
  sampleForm.department = template.department
  ElMessage.success(`已应用"${template.name}"模板`)
}

// 返回
const goBack = () => {
  router.push('/sample')
}

// 提交
const handleSubmit = async () => {
  submitting.value = true
  try {
    // 调用真实后端API创建标本
    await sampleService.createSample({
      ...sampleForm,
      testItems: sampleForm.testItems.join(',')
    })
    ElMessage.success('标本创建成功！')
    router.push('/sample')
  } catch (error) {
    // 显示后端返回的错误信息
    const errorMessage = error?.response?.data?.message || error?.message || '创建失败，请重试'
    ElMessage.error(errorMessage)
  } finally {
    submitting.value = false
  }
}

// 提交并继续
const handleSubmitAndContinue = async () => {
  submitting.value = true
  try {
    // 调用真实后端API创建标本
    await sampleService.createSample({
      ...sampleForm,
      testItems: sampleForm.testItems.join(',')
    })
    ElMessage.success('标本创建成功！可以继续创建')
    generateSampleNo()
    sampleForm.patientName = ''
    sampleForm.patientId = ''
    sampleForm.age = ''
    sampleForm.phone = ''
    sampleForm.diagnosis = ''
    sampleForm.testItems = []
    selectedTestCategories.value = []
  } catch (error) {
    // 显示后端返回的错误信息
    const errorMessage = error?.response?.data?.message || error?.message || '创建失败，请重试'
    ElMessage.error(errorMessage)
  } finally {
    submitting.value = false
  }
}

// 生命周期
onMounted(() => {
  generateSampleNo()
  sampleForm.collectTime = new Date().toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).replace(/\//g, '-')
})
</script>

<style scoped>
.professional-create-container {
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

/* 提示框 */
.tip-alert {
  margin-bottom: 20px;
  border-radius: 12px;
}

/* 表单容器 */
.form-container {
  margin-bottom: 20px;
}

.form-card {
  border-radius: 12px;
}

/* 表单分区 */
.form-section {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px dashed #EBEEF5;
}

.form-section:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 生成图标 */
.generate-icon {
  cursor: pointer;
  color: #409EFF;
  transition: transform 0.3s;
}

.generate-icon:hover {
  transform: rotate(180deg);
}

/* 检验项目选择 */
.selected-items-preview {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-top: 12px;
}

.preview-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
  display: block;
}

/* 提交按钮 */
.form-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding-top: 24px;
  border-top: 1px solid #EBEEF5;
}

/* 模板卡片 */
.template-card {
  border-radius: 12px;
}

.template-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.template-tag {
  cursor: pointer;
  padding: 8px 16px;
  font-size: 14px;
  transition: all 0.2s;
}

.template-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 响应式 */
@media (max-width: 768px) {
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions .el-button {
    width: 100%;
  }
}
</style>
