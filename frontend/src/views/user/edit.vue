<template>
  <div class="professional-user-edit-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div class="header-title">
          <h1 class="page-title">
            <el-icon><Edit /></el-icon>
            编辑用户
          </h1>
          <p class="page-subtitle">修改用户信息</p>
        </div>
      </div>
    </div>

    <!-- 提示 -->
    <el-alert title="修改密码或角色需要谨慎操作" type="warning" :closable="false" show-icon class="tip-alert" />

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
              <el-form-item label="用户名">
                <el-input v-model="userForm.username" disabled />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="真实姓名" prop="realName">
                <el-input v-model="userForm.realName" placeholder="请输入真实姓名" clearable />
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
                <el-input v-model="userForm.phone" placeholder="请输入手机号" clearable />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="邮箱">
                <el-input v-model="userForm.email" placeholder="请输入邮箱" clearable />
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

        <!-- 密码重置 -->
        <div class="form-section">
          <div class="section-header">
            <el-icon><Lock /></el-icon>
            <span>密码管理</span>
          </div>
          
          <el-row :gutter="24">
            <el-col :span="24">
              <el-form-item label="重置密码">
                <el-button type="warning" @click="resetPassword">
                  <el-icon><Refresh /></el-icon>
                  重置为默认密码
                </el-button>
                <span class="tip-text">重置后密码将变为: 123456</span>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 提交按钮 -->
        <div class="form-actions">
          <el-button @click="goBack" size="large">取消</el-button>
          <el-button type="primary" size="large" @click="handleSubmit" :loading="submitting">
            <el-icon><Check /></el-icon>
            保存修改
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Edit, User, Phone, OfficeBuilding, Lock, Refresh, Check } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userFormRef = ref(null)
const submitting = ref(false)

const userForm = reactive({
  id: 1,
  username: 'admin',
  realName: '系统管理员',
  role: 'ADMIN',
  phone: '13800000001',
  email: 'admin@lab.com',
  department: '信息中心',
  status: 1
})

const userRules = {
  realName: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择用户角色', trigger: 'change' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

const goBack = () => {
  router.push('/user')
}

const resetPassword = () => {
  ElMessageBox.confirm('确定重置该用户密码吗？重置后密码将变为默认密码: 123456', '重置密码', { type: 'warning' })
    .then(() => {
      ElMessage.success('密码已重置为: 123456')
    }).catch(() => {})
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('用户信息已保存')
    router.push('/user')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  if (route.params.id) {
    userForm.id = parseInt(route.params.id)
  }
})
</script>

<style scoped>
.professional-user-edit-container {
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
  border-left: 3px solid #E6A23C;
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

.status-text, .tip-text {
  margin-left: 12px;
  color: #909399;
  font-size: 13px;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding-top: 24px;
}
</style>
