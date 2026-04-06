<template>
  <div class="professional-login-container">
    <div class="login-wrapper">
      <!-- 左侧品牌区域 -->
      <div class="brand-section">
        <div class="brand-content">
          <div class="logo">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          <h1 class="brand-title">医学实验室管理系统</h1>
          <p class="brand-subtitle">Laboratory Information Management System</p>
          
          <div class="features">
            <div class="feature-item">
              <el-icon><Box /></el-icon>
              <span>标本全流程追踪</span>
            </div>
            <div class="feature-item">
              <el-icon><Document /></el-icon>
              <span>报告智能审核</span>
            </div>
            <div class="feature-item">
              <el-icon><Cpu /></el-icon>
              <span>AI辅助诊断</span>
            </div>
            <div class="feature-item">
              <el-icon><Connection /></el-icon>
              <span>HL7标准接口</span>
            </div>
          </div>
        </div>
        <div class="brand-footer">
          <p>© 2026 医学实验室管理系统 v1.0</p>
        </div>
      </div>

      <!-- 右侧登录区域 -->
      <div class="login-section">
        <div class="login-card">
          <div class="login-header">
            <h2>用户登录</h2>
            <p>请输入您的账号信息登录系统</p>
          </div>

          <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" size="large">
            <el-form-item prop="username">
              <el-input 
                v-model="loginForm.username" 
                placeholder="请输入用户名"
                prefix-icon="User"
                clearable
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input 
                v-model="loginForm.password" 
                type="password"
                placeholder="请输入密码"
                prefix-icon="Lock"
                show-password
                @keyup.enter="handleLogin"
              />
            </el-form-item>

            <div class="form-options">
              <el-checkbox v-model="rememberMe">记住我</el-checkbox>
              <el-link type="primary">忘记密码？</el-link>
            </div>

            <el-form-item>
              <el-button type="primary" size="large" class="login-button" @click="handleLogin" :loading="loading">
                <span v-if="!loading">登 录</span>
                <span v-else>登录中...</span>
              </el-button>
            </el-form-item>
          </el-form>

          <div class="login-footer">
            <span>还没有账号？</span>
            <el-link type="primary" @click="goToRegister">立即注册</el-link>
          </div>
        </div>

        <!-- 演示账号提示 -->
        <div class="demo-hint">
          <el-alert title="演示账号: admin / admin123" type="info" :closable="false" show-icon />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, OfficeBuilding, Box, Document, Cpu, Connection } from '@element-plus/icons-vue'
import userService from '@/services/userService'
import { useUserStore } from '@/stores'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref(null)
const loading = ref(false)
const rememberMe = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码长度至少为8位', trigger: 'blur' },
    {
      pattern: /^(?=.*[a-zA-Z])(?=.*\d)/,
      message: '密码需包含字母和数字',
      trigger: 'blur'
    }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      // 调用真实后端API
      const response = await userService.login(loginForm.username, loginForm.password)

      // 存储token和用户信息到Pinia store
      userStore.setToken(response.token)
      userStore.setUser(response.user)

      ElMessage.success('登录成功！')
      router.push('/')
    } catch (error) {
      // 错误信息由 request.ts 拦截器统一显示，此处无需重复处理
      console.error('登录失败:', error)
    } finally {
      loading.value = false
    }
  })
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.professional-login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}

.login-wrapper {
  display: flex;
  width: 1000px;
  min-height: 600px;
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
}

/* 左侧品牌区域 */
.brand-section {
  flex: 1;
  background: linear-gradient(135deg, #409EFF, #66b1ff);
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
  line-height: 1.3;
}

.brand-subtitle {
  font-size: 14px;
  opacity: 0.9;
  margin: 0 0 40px;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 16px;
  opacity: 0.95;
}

.feature-item .el-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-footer {
  font-size: 12px;
  opacity: 0.7;
  text-align: center;
}

/* 右侧登录区域 */
.login-section {
  width: 420px;
  padding: 60px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-header {
  margin-bottom: 40px;
  text-align: center;
}

.login-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 10px;
}

.login-header p {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.login-button {
  width: 100%;
  height: 50px;
  font-size: 18px;
  font-weight: 600;
  border-radius: 10px;
}

.login-footer {
  text-align: center;
  margin-top: 30px;
  color: #909399;
}

.login-footer .el-link {
  margin-left: 5px;
}

.demo-hint {
  margin-top: 20px;
}

@media (max-width: 1000px) {
  .login-wrapper {
    width: 90%;
    flex-direction: column;
  }
  
  .brand-section {
    display: none;
  }
  
  .login-section {
    width: 100%;
    padding: 40px 30px;
  }
}
</style>
