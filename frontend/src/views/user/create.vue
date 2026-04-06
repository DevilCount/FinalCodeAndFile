<template>
  <div class="professional-user-create-container">
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
            新建用户
          </h1>
          <p class="page-subtitle">创建系统用户账号</p>
        </div>
      </div>
    </div>

    <!-- 提示 -->
    <el-alert title="新建用户将自动生成初始密码: 123456" type="info" :closable="false" show-icon class="tip-alert" />

    <!-- 表单 -->
    <el-card shadow="hover" class="form-card">
      <el-form ref="userFormRef" :model="userForm" :rules="userRules" label-width="140px" size="large">
        <!-- 基本信息 -->
        <div class="form-section">
          <div class="section-header">
            <el-icon><User /></el-icon>
            <span>基本信息</span>
          </div>
          
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="用户名" prop="username">
                <el-input v-model="userForm.username" placeholder="请输入用户名" clearable>
                  <template #prefix><el-icon><User /></el-icon></template>
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="真实姓名" prop="realName">
                <el-input v-model="userForm.realName" placeholder="请输入真实姓名" clearable>
                  <template #prefix><el-icon><Postcard /></el-icon></template>
                </el-input>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="角色" prop="role">
                <el-select v-model="userForm.role" placeholder="请选择用户角色" style="width: 100%">
                  <el-option label="👑 管理员" value="ADMIN" />
                  <el-option label="👨‍⚕️ 医生" value="DOCTOR" />
                  <el-option label="🔬 检验技师" value="LAB_TECHNICIAN" />
                  <el-option label="👤 普通用户" value="USER" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="状态">
                <el-switch v-model="userForm.status" :active-value="1" :inactive-value="0" />
                <span class="status-text">{{ userForm.status === 1 ? '启用' : '禁用' }}</span>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 联系信息 -->
        <div class="form-section">
          <div class="section-header">
            <el-icon><Phone /></el-icon>
            <span>联系信息</span>
          </div>
          
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="手机号" prop="phone">
                <el-input v-model="userForm.phone" placeholder="请输入手机号" clearable>
                  <template #prefix><el-icon><Phone /></el-icon></template>
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="邮箱">
                <el-input v-model="userForm.email" placeholder="请输入邮箱" clearable>
                  <template #prefix><el-icon><Message /></el-icon></template>
                </el-input>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 科室信息 -->
        <div class="form-section">
          <div class="section-header">
            <el-icon><OfficeBuilding /></el-icon>
            <span>科室信息</span>
          </div>
          
          <el-row :gutter="24">
            <el-col :span="24">
              <el-form-item label="所属科室" prop="department">
                <el-select v-model="userForm.department" placeholder="请选择或输入科室" style="width: 100%" filterable allow-create>
                  <el-option label="内科" value="内科" />
                  <el-option label="外科" value="外科" />
                  <el-option label="儿科" value="儿科" />
                  <el-option label="妇产科" value="妇产科" />
                  <el-option label="急诊科" value="急诊科" />
                  <el-option label="检验科" value="检验科" />
                  <el-option label="体检科" value="体检科" />
                  <el-option label="信息中心" value="信息中心" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 提交按钮 -->
        <div class="form-actions">
          <el-button @click="goBack" size="large">取消</el-button>
          <el-button type="primary" size="large" @click="handleSubmit" :loading="submitting">
            <el-icon><Check /></el-icon>
            创建用户
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Plus, User, Postcard, Phone, Message, OfficeBuilding, Check } from '@element-plus/icons-vue'

const router = useRouter()
const userFormRef = ref(null)
const submitting = ref(false)

const userForm = reactive({
  username: '',
  realName: '',
  role: '',
  phone: '',
  email: '',
  department: '',
  status: 1
})

const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' }
  ],
  realName: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择用户角色', trigger: 'change' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  department: [
    { required: true, message: '请选择所属科室', trigger: 'change' }
  ]
}

const goBack = () => {
  router.push('/user')
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('用户创建成功！初始密码为: 123456')
    router.push('/user')
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.professional-user-create-container {
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

.tip-alert {
  margin-bottom: 20px;
  border-radius: 12px;
}

.form-card {
  border-radius: 12px;
}

.form-section {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px dashed #EBEEF5;
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

.status-text {
  margin-left: 12px;
  color: #606266;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding-top: 24px;
}
</style>
