<template>
  <div class="professional-register-container">
    <div class="register-wrapper">
      <!-- 左侧品牌区域 -->
      <div class="brand-section">
        <div class="brand-content">
          <div class="logo">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          <h1 class="brand-title">加入我们</h1>
          <p class="brand-subtitle">创建您的实验室管理系统账号</p>
          
          <div class="benefits">
            <div class="benefit-item">
              <el-icon><CircleCheck /></el-icon>
              <span>全流程标本管理</span>
            </div>
            <div class="benefit-item">
              <el-icon><CircleCheck /></el-icon>
              <span>智能报告生成</span>
            </div>
            <div class="benefit-item">
              <el-icon><CircleCheck /></el-icon>
              <span>AI辅助诊断</span>
            </div>
          </div>
        </div>
        <div class="brand-footer">
          <el-button text @click="goToLogin" class="back-link">
            <el-icon><ArrowLeft /></el-icon>
            返回登录
          </el-button>
        </div>
      </div>

      <!-- 右侧注册区域 -->
      <div class="register-section">
        <div class="register-card">
          <div class="register-header">
            <h2>用户注册</h2>
            <p>创建新账号，开始使用系统</p>
          </div>

          <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules" size="large">
            <el-form-item prop="username">
              <el-input 
                v-model="registerForm.username" 
                placeholder="请输入用户名"
                prefix-icon="User"
                clearable
              />
            </el-form-item>
            
            <el-form-item prop="realName">
              <el-input 
                v-model="registerForm.realName" 
                placeholder="请输入真实姓名"
                prefix-icon="Postcard"
                clearable
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input 
                v-model="registerForm.password" 
                type="password"
                placeholder="请输入密码"
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>

            <el-form-item prop="confirmPassword">
              <el-input 
                v-model="registerForm.confirmPassword" 
                type="password"
                placeholder="请确认密码"
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>

            <el-form-item prop="role">
              <el-select v-model="registerForm.role" placeholder="请选择用户角色" style="width: 100%">
                <el-option label="👨‍⚕️ 医生" value="DOCTOR" />
                <el-option label="🔬 检验技师" value="LAB_TECHNICIAN" />
                <el-option label="👤 普通用户" value="USER" />
              </el-select>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" size="large" class="register-button" @click="handleRegister" :loading="loading">
                <span v-if="!loading">注 册</span>
                <span v-else>注册中...</span>
              </el-button>
            </el-form-item>
          </el-form>

          <div class="register-footer">
            <span>已有账号？</span>
            <el-link type="primary" @click="goToLogin">立即登录</el-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Postcard, CircleCheck, ArrowLeft, OfficeBuilding } from '@element-plus/icons-vue'
import userService from '@/services/userService'

const router = useRouter()

const registerFormRef = ref(null)
const loading = ref(false)

const registerForm = reactive({
  username: '',
  realName: '',
  password: '',
  confirmPassword: '',
  role: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' }
  ],
  realName: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择用户角色', trigger: 'change' }
  ]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      // 调用真实后端API进行注册
      await userService.register({
        username: registerForm.username,
        realName: registerForm.realName,
        password: registerForm.password,
        role: registerForm.role
      })
      ElMessage.success('注册成功！请登录')
      router.push('/login')
    } catch (error) {
      // 显示后端返回的错误信息
      const errorMessage = error?.response?.data?.message || error?.message || '注册失败，请重试'
      ElMessage.error(errorMessage)
    } finally {
      loading.value = false
    }
  })
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.professional-register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-wrapper {
  display: flex;
  width: 1000px;
  min-height: 600px;
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
}

.brand-section {
  flex: 1;
  background: linear-gradient(135deg, #667eea, #764ba2);
  padding: 60px 40px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: white;
}

.brand-content {
  flex: 1;
}

.logo {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  margin-bottom: 30px;
}

.brand-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 10px;
}

.brand-subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin: 0 0 40px;
}

.benefits {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.benefit-item {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 16px;
}

.benefit-item .el-icon {
  font-size: 24px;
  color: #67C23A;
}

.brand-footer {
  padding-top: 20px;
}

.back-link {
  color: white;
  font-size: 16px;
}

.back-link:hover {
  color: rgba(255, 255, 255, 0.8);
}

.register-section {
  width: 420px;
  padding: 60px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.register-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.register-header {
  margin-bottom: 40px;
  text-align: center;
}

.register-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 10px;
}

.register-header p {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.register-button {
  width: 100%;
  height: 50px;
  font-size: 18px;
  font-weight: 600;
  border-radius: 10px;
}

.register-footer {
  text-align: center;
  margin-top: 30px;
  color: #909399;
}

@media (max-width: 1000px) {
  .register-wrapper {
    width: 90%;
    flex-direction: column;
  }
  
  .brand-section {
    display: none;
  }
  
  .register-section {
    width: 100%;
    padding: 40px 30px;
  }
}
</style>
