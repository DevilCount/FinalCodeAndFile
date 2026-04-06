<template>
  <div class="layout-container">
    <!-- 医疗系统专业侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: isCollapse }">
      <!-- 医院Logo和名称 -->
      <div class="sidebar-header">
        <div class="hospital-logo">
          <div class="logo-icon">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          <div class="hospital-info" v-if="!isCollapse">
            <h2 class="hospital-name">{{ hospitalName }}</h2>
            <p class="hospital-department">检验科管理系统</p>
          </div>
        </div>
      </div>
      
      <!-- 医疗系统菜单分组 -->
      <nav class="sidebar-nav">
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          router
          :collapse="isCollapse"
          :unique-opened="true"
        >
          <!-- 核心业务模块 -->
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <template #title>
              <span>工作台</span>
            </template>
          </el-menu-item>
          
          <!-- 检验管理分组 -->
          <el-sub-menu index="1">
            <template #title>
              <el-icon><Box /></el-icon>
              <span>检验管理</span>
            </template>
            <el-menu-item index="/sample">
              <el-icon><Box /></el-icon>
              <template #title>
                <span>标本管理</span>
                <el-tag v-if="pendingSamplesCount > 0" size="small" type="danger" class="menu-badge">
                  {{ pendingSamplesCount }}
                </el-tag>
              </template>
            </el-menu-item>
            <el-menu-item index="/sample/receive" disabled>
              <el-icon><Check /></el-icon>
              <span>标本签收</span>
            </el-menu-item>
            <el-menu-item index="/sample/testing" disabled>
              <el-icon><Search /></el-icon>
              <span>检验处理</span>
            </el-menu-item>
            <el-menu-item index="/sample/quality" disabled>
              <el-icon><Finished /></el-icon>
              <span>质控管理</span>
            </el-menu-item>
          </el-sub-menu>
          
          <!-- 报告管理分组 -->
          <el-sub-menu index="2">
            <template #title>
              <el-icon><Document /></el-icon>
              <span>报告管理</span>
            </template>
            <el-menu-item index="/report">
              <el-icon><Tickets /></el-icon>
              <span>报告列表</span>
            </el-menu-item>
            <el-menu-item index="/report/review" disabled>
              <el-icon><EditPen /></el-icon>
              <span>报告审核</span>
            </el-menu-item>
            <el-menu-item index="/report/print" disabled>
              <el-icon><Printer /></el-icon>
              <span>报告打印</span>
            </el-menu-item>
            <el-menu-item index="/report/archive" disabled>
              <el-icon><Folder /></el-icon>
              <span>报告归档</span>
            </el-menu-item>
          </el-sub-menu>
          
          <!-- 智能辅助分组 -->
          <el-sub-menu index="3">
            <template #title>
              <el-icon><Cpu /></el-icon>
              <span>智能辅助</span>
            </template>
            <el-menu-item index="/ai">
              <el-icon><MagicStick /></el-icon>
              <span>AI诊断</span>
            </el-menu-item>
            <el-menu-item index="/ai/consult" disabled>
              <el-icon><ChatDotRound /></el-icon>
              <span>智能咨询</span>
            </el-menu-item>
            <el-menu-item index="/statistics" disabled>
              <el-icon><TrendCharts /></el-icon>
              <span>统计分析</span>
            </el-menu-item>
            <el-menu-item index="/dashboard">
              <el-icon><DataAnalysis /></el-icon>
              <span>数据看板</span>
            </el-menu-item>
          </el-sub-menu>
          
          <!-- 系统管理分组 -->
          <el-sub-menu index="4">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>系统管理</span>
            </template>
            <el-menu-item index="/user">
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            <el-menu-item index="/equipment" disabled>
              <el-icon><Monitor /></el-icon>
              <span>设备管理</span>
            </el-menu-item>
            <el-menu-item index="/system/config" disabled>
              <el-icon><Tools /></el-icon>
              <span>系统配置</span>
            </el-menu-item>
            <el-menu-item index="/system/log" disabled>
              <el-icon><Notebook /></el-icon>
              <span>操作日志</span>
            </el-menu-item>
          </el-sub-menu>
        </el-menu>
      </nav>
      
      <!-- 用户信息卡片 -->
      <div class="user-card" v-if="!isCollapse">
        <div class="user-avatar">
          <el-avatar :size="48" :src="userAvatar">
            {{ userInitial }}
          </el-avatar>
        </div>
        <div class="user-details">
          <h3 class="user-name">{{ userName }}</h3>
          <p class="user-role">{{ userRole }}</p>
          <div class="user-status">
            <el-tag :type="userStatus === '在线' ? 'success' : 'info'" size="small">
              {{ userStatus }}
            </el-tag>
          </div>
        </div>
      </div>
    </aside>
    
    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 顶部导航栏 -->
      <header class="main-header">
        <div class="header-left">
          <el-button
            type="text"
            @click="toggleSidebar"
            class="sidebar-toggle"
            circle
          >
            <el-icon><Menu /></el-icon>
          </el-button>
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-for="item in breadcrumb" :key="item.path">
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-center">
          <div class="system-status">
            <el-tooltip content="Redis缓存状态" placement="bottom">
              <el-tag :type="redisStatus ? 'success' : 'danger'" size="small" class="status-tag">
                <el-icon><Connection /></el-icon>
                {{ redisStatus ? '缓存正常' : '缓存异常' }}
              </el-tag>
            </el-tooltip>
            <el-tooltip content="系统时间" placement="bottom">
              <el-tag type="info" size="small" class="status-tag">
                <el-icon><Clock /></el-icon>
                {{ currentTime }}
              </el-tag>
            </el-tooltip>
          </div>
        </div>
        
        <div class="header-right">
          <!-- 通知中心 -->
          <el-dropdown trigger="click" class="notification-dropdown">
            <el-badge :value="notificationCount" :max="99" :hidden="notificationCount === 0">
              <el-button type="text" circle>
                <el-icon><Bell /></el-icon>
              </el-button>
            </el-badge>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-for="(item, index) in notifications" :key="index">
                  <div class="notification-item">
                    <div class="notification-title">
                      <el-icon :color="item.type === 'warning' ? '#e6a23c' : '#409eff'">
                        <component :is="item.icon" />
                      </el-icon>
                      <span>{{ item.title }}</span>
                    </div>
                    <div class="notification-time">{{ item.time }}</div>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item v-if="notifications.length === 0" disabled>
                  暂无新通知
                </el-dropdown-item>
                <el-dropdown-item divided @click="clearNotifications">
                  <el-icon><Delete /></el-icon>
                  清空通知
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          
          <!-- 用户菜单 -->
          <el-dropdown trigger="click" class="user-dropdown">
            <div class="user-profile">
              <el-avatar :size="36" :src="userAvatar">
                {{ userInitial }}
              </el-avatar>
              <div class="user-profile-info">
                <div class="user-profile-name">{{ userName }}</div>
                <div class="user-profile-role">{{ userRole }}</div>
              </div>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleProfile">
                  <el-icon><User /></el-icon>
                  <span>个人中心</span>
                </el-dropdown-item>
                <el-dropdown-item @click="handleSettings">
                  <el-icon><Setting /></el-icon>
                  <span>账户设置</span>
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      
      <!-- 内容区域 -->
      <div class="content-wrapper">
        <router-view />
      </div>
      
      <!-- 页脚 -->
      <footer class="main-footer">
        <div class="footer-content">
          <p>{{ hospitalName }} 检验科管理系统 &copy; {{ currentYear }} - 基于微服务架构的实验室管理系统</p>
          <p class="system-info">
            <span>版本: {{ systemVersion }}</span>
            <span> | </span>
            <span>Redis状态: <span :class="redisStatus ? 'status-success' : 'status-error'">{{ redisStatus ? '正常' : '异常' }}</span></span>
          </p>
        </div>
      </footer>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores'
import {
  OfficeBuilding, HomeFilled, Box, Check, Search, Finished,
  Document, Tickets, EditPen, Printer, Folder,
  Cpu, MagicStick, ChatDotRound, TrendCharts, DataAnalysis,
  Setting, Monitor, Tools, Notebook,
  Menu, ArrowDown, Connection, Clock, Bell, Delete,
  SwitchButton
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const isCollapse = ref(false)

// 医院信息
const hospitalName = ref('阳光医院')
const activeMenu = computed(() => route.path)
const userInitial = computed(() => {
  const name = userStore.userName || '未知用户'
  return name ? name.charAt(0).toUpperCase() : 'U'
})
const userName = computed(() => userStore.userName || '检验员')
const userAvatar = computed(() => (userStore.user as any)?.avatar || '')
const userRole = computed(() => {
  const role = (userStore.userRole || '') as string
  if (role === 'admin' || role === 'ADMIN') return '系统管理员'
  if (role === 'doctor' || role === 'DOCTOR') return '医师'
  if (role === 'technician' || role === 'TECHNICIAN' || role === 'LAB_TECHNICIAN') return '检验技师'
  if (role === 'reception' || role === 'NURSE') return '前台接待'
  return role ? role : '检验员'
})
const userStatus = computed(() => userStore.user?.status || '在线')

// 系统状态
const redisStatus = ref(true)
const currentTime = ref('')
const currentYear = ref(new Date().getFullYear())
const systemVersion = ref('v1.0.0')
const notificationCount = ref(3)
const notifications = ref([
  { id: 1, title: '标本20240329001已签收', type: 'info', icon: 'Check', time: '10分钟前' },
  { id: 2, title: '检验报告20240329002等待审核', type: 'warning', icon: 'Warning', time: '25分钟前' },
  { id: 3, title: '系统缓存已优化，性能提升45%', type: 'info', icon: 'InfoFilled', time: '1小时前' }
])

// 标本状态
const pendingSamplesCount = ref(5)

// 面包屑导航
const breadcrumb = computed(() => {
  const path = route.path
  const segments = path.split('/').filter(segment => segment)
  
  const breadcrumbMap = {
    'sample': '标本管理',
    'report': '报告管理',
    'ai': 'AI诊断',
    'user': '用户管理',
    'system': '系统设置',
    'dashboard': '数据看板',
    'statistics': '统计分析'
  }
  
  return segments.map(segment => ({
    path: '/' + segment,
    title: (breadcrumbMap as Record<string, string>)[segment] || segment
  }))
})

// 方法
const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const handleProfile = () => {
  router.push('/profile')
}

const handleSettings = () => {
  router.push('/settings')
}

const handleLogout = () => {
  // 调用userStore的logout方法
  userStore.logout()
  // 跳转到登录页面
  router.push('/login')
}

const clearNotifications = () => {
  notificationCount.value = 0
  notifications.value = []
}

// 更新当前时间
const updateCurrentTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { 
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 检查Redis状态
const checkRedisStatus = async () => {
  try {
    // 这里可以调用API检查Redis状态
    // 暂时模拟检查
    redisStatus.value = true
  } catch (error) {
    redisStatus.value = false
  }
}

// 定时器引用
let timeInterval: ReturnType<typeof setInterval>
let redisInterval: ReturnType<typeof setInterval>

// 生命周期
onMounted(() => {
  // 检查登录状态
  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/login')
  }

  // 初始化时间
  updateCurrentTime()
  timeInterval = setInterval(updateCurrentTime, 1000)

  // 检查Redis状态
  checkRedisStatus()
  redisInterval = setInterval(checkRedisStatus, 30000)

  // 模拟获取待处理标本数量
  // 实际项目中这里应该调用API
  setTimeout(() => {
    pendingSamplesCount.value = Math.floor(Math.random() * 10) + 1
  }, 1000)
})

onUnmounted(() => {
  clearInterval(timeInterval)
  clearInterval(redisInterval)
})
</script>

<style lang="scss" scoped>
.layout-container {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  font-family: var(--font-family);
}

// ==================== 侧边栏样式 - 医疗专业设计 ====================
.sidebar {
  width: 270px;
  height: 100%;
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 50%, #334155 100%);
  color: #fff;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  box-shadow: 4px 0 24px rgba(15, 23, 42, 0.15);
  position: relative;
  z-index: 1; // 降低z-index,避免遮挡主内容区
  
  &.collapsed {
    width: 72px;
    
    .hospital-info,
    .user-details {
      display: none;
    }
    
    .logo-icon {
      margin: 0 auto;
    }
  }
  
  // 侧边栏头部
  .sidebar-header {
    padding: 28px 24px 20px;
    border-bottom: 1px solid rgba(148, 163, 184, 0.15);
    position: relative;
    
    &::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 24px;
      right: 24px;
      height: 1px;
      background: linear-gradient(90deg, transparent, rgba(96, 165, 250, 0.5), transparent);
    }
    
    .hospital-logo {
      display: flex;
      align-items: center;
      gap: 14px;
      
      .logo-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #1e88e5 0%, #42a5f5 50%, #7c3aed 100%);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        box-shadow: 0 8px 24px rgba(30, 136, 229, 0.3);
        
        .el-icon {
          font-size: 26px;
          color: white;
        }
      }
      
      .hospital-info {
        .hospital-name {
          margin: 0;
          font-size: 17px;
          font-weight: var(--font-weight-bold);
          color: white;
          line-height: 1.4;
          letter-spacing: -0.3px;
        }
        
        .hospital-department {
          margin: 6px 0 0 0;
          font-size: 12px;
          color: rgba(148, 163, 184, 0.9);
          line-height: 1.3;
          letter-spacing: 0.3px;
          text-transform: uppercase;
        }
      }
    }
  }
  
  // 侧边栏导航
  .sidebar-nav {
    flex: 1;
    overflow-y: auto;
    padding: 20px 12px;
    
    &::-webkit-scrollbar {
      width: 4px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: rgba(148, 163, 184, 0.2);
      border-radius: 2px;
    }
    
    .sidebar-menu {
      border-right: none;
      background-color: transparent;
      
      :deep(.el-sub-menu__title),
      :deep(.el-menu-item) {
        height: 50px;
        line-height: 50px;
        color: rgba(203, 213, 225, 0.9);
        border-radius: 10px;
        margin: 2px 0;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        padding: 0 12px;
        
        &:hover {
          background-color: rgba(148, 163, 184, 0.12);
          color: white;
        }
        
        &.is-active {
          background: linear-gradient(135deg, rgba(30, 136, 229, 0.25) 0%, rgba(124, 58, 237, 0.15) 100%);
          color: #60a5fa;
          border: 1px solid rgba(96, 165, 250, 0.25);
          box-shadow: 0 4px 12px rgba(30, 136, 229, 0.15);
          
          .el-icon {
            color: #60a5fa;
          }
        }
        
        .el-icon {
          color: rgba(148, 163, 184, 0.8);
          width: 20px;
          margin-right: 12px;
        }
      }
      
      :deep(.el-sub-menu) {
        &.is-active > .el-sub-menu__title {
          color: #60a5fa;
          background-color: rgba(30, 136, 229, 0.1);

          .el-icon {
            color: #60a5fa;
          }
        }

        // 优化:非展开状态的子菜单标题不拦截点击事件
        &:not(.is-opened) > .el-sub-menu__title {
          pointer-events: none;

          // 恢复内部图标的点击能力
          .el-icon,
          span {
            pointer-events: auto;
          }
        }

        :deep(.el-menu--inline) {
          padding: 0 0 0 12px;
          
          .el-menu-item {
            font-size: 13px;
            height: 44px;
            line-height: 44px;
          }
        }
      }
      
      .menu-badge {
        margin-left: auto;
        height: 20px;
        line-height: 18px;
        font-size: 11px;
        padding: 0 7px;
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        border: none;
        font-weight: var(--font-weight-semibold);
      }
    }
  }
  
  // 用户信息卡片
  .user-card {
    padding: 20px 20px 24px;
    border-top: 1px solid rgba(148, 163, 184, 0.15);
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.5) 0%, rgba(30, 41, 59, 0.8) 100%);
    position: relative;
    
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 20px;
      right: 20px;
      height: 1px;
      background: linear-gradient(90deg, transparent, rgba(96, 165, 250, 0.3), transparent);
    }
    
    .user-avatar {
      margin-bottom: 14px;
      
      .el-avatar {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        border: 2px solid rgba(96, 165, 250, 0.3);
      }
    }
    
    .user-details {
      .user-name {
        margin: 0 0 4px 0;
        font-size: 15px;
        font-weight: var(--font-weight-semibold);
        color: white;
        letter-spacing: -0.2px;
      }
      
      .user-role {
        margin: 0 0 10px 0;
        font-size: 12px;
        color: rgba(148, 163, 184, 0.9);
      }
      
      .user-status {
        display: inline-block;
        
        .el-tag {
          height: 22px;
          line-height: 20px;
          font-size: 11px;
          padding: 0 10px;
          font-weight: var(--font-weight-medium);
          background: rgba(34, 197, 94, 0.15);
          border: 1px solid rgba(34, 197, 94, 0.3);
          color: #4ade80;
        }
      }
    }
  }
}

// ==================== 主内容区样式 ====================
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  background: linear-gradient(180deg, var(--bg-color) 0%, var(--bg-secondary) 100%);
  position: relative;
  z-index: 2; // 确保主内容区的可点击元素高于侧边栏
  
  // 顶部导航栏
  .main-header {
    height: 68px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.98) 100%);
    backdrop-filter: blur(20px);
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05), 0 1px 2px rgba(15, 23, 42, 0.03);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 28px;
    z-index: var(--z-sticky);
    border-bottom: 1px solid var(--border-light);
    
    .header-left {
      display: flex;
      align-items: center;
      gap: 20px;
      
      .sidebar-toggle {
        font-size: 22px;
        color: var(--text-secondary);
        width: 40px;
        height: 40px;
        border-radius: 10px;
        transition: all 0.2s;
        
        &:hover {
          background-color: var(--bg-secondary);
          color: var(--primary-color);
        }
      }
      
      .breadcrumb {
        :deep(.el-breadcrumb__inner) {
          font-size: 14px;
          color: var(--text-tertiary);
          font-weight: var(--font-weight-medium);
          
          &.is-link {
            color: var(--primary-color);
            font-weight: var(--font-weight-semibold);
            
            &:hover {
              color: var(--primary-dark);
            }
          }
        }
        
        :deep(.el-breadcrumb__item) {
          .el-icon {
            color: var(--text-light);
          }
        }
      }
    }
    
    .header-center {
      .system-status {
        display: flex;
        align-items: center;
        gap: 10px;
        
        .status-tag {
          height: 32px;
          line-height: 30px;
          font-size: 12px;
          padding: 0 14px;
          border-radius: 16px;
          font-weight: var(--font-weight-medium);
          border: none;
          
          .el-icon {
            margin-right: 5px;
            font-size: 13px;
          }
        }
      }
    }
    
    .header-right {
      display: flex;
      align-items: center;
      gap: 18px;
      
      .notification-dropdown {
        .el-badge {
          .el-button {
            width: 42px;
            height: 42px;
            font-size: 20px;
            color: var(--text-secondary);
            border-radius: 10px;
            transition: all 0.2s;
            
            &:hover {
              background-color: var(--bg-secondary);
              color: var(--primary-color);
            }
          }
        }
        
        .notification-item {
          min-width: 280px;
          padding: 12px 0;
          
          .notification-title {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 14px;
            color: var(--text-primary);
            margin-bottom: 6px;
            font-weight: var(--font-weight-medium);
            
            .el-icon {
              font-size: 16px;
            }
          }
          
          .notification-time {
            font-size: 12px;
            color: var(--text-light);
            text-align: right;
          }
        }
      }
      
      .user-dropdown {
        cursor: pointer;
        
        .user-profile {
          display: flex;
          align-items: center;
          gap: 14px;
          padding: 6px 10px;
          border-radius: 12px;
          transition: all 0.2s;
          
          &:hover {
            background-color: var(--bg-secondary);
          }
          
          .el-avatar {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
          }
          
          .user-profile-info {
            text-align: left;
            
            .user-profile-name {
              font-size: 14px;
              font-weight: var(--font-weight-semibold);
              color: var(--text-primary);
              line-height: 1.4;
            }
            
            .user-profile-role {
              font-size: 12px;
              color: var(--text-light);
              line-height: 1.3;
            }
          }
          
          .el-icon {
            color: var(--text-light);
            font-size: 12px;
            transition: transform 0.2s;
          }
        }
      }
    }
  }
  
  // 内容包裹区
  .content-wrapper {
    flex: 1;
    padding: 28px;
    overflow-y: auto;
    background: transparent;
  }
  
  // 页脚
  .main-footer {
    height: 52px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.98) 100%);
    border-top: 1px solid var(--border-light);
    display: flex;
    align-items: center;
    justify-content: center;
    
    .footer-content {
      text-align: center;
      
      p {
        margin: 0;
        font-size: 12px;
        color: var(--text-light);
        line-height: 1.6;
      }
      
      .system-info {
        margin-top: 4px;
        
        .status-success {
          color: var(--success-color);
          font-weight: var(--font-weight-semibold);
        }
        
        .status-error {
          color: var(--danger-color);
          font-weight: var(--font-weight-semibold);
        }
      }
    }
  }
}

// ==================== 响应式调整 ====================
@media (max-width: 1200px) {
  .sidebar {
    width: 250px;
    
    &.collapsed {
      width: 72px;
    }
  }
}

@media (max-width: 992px) {
  .main-header {
    .header-center {
      display: none;
    }
    
    padding: 0 20px;
  }
  
  .content-wrapper {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    position: absolute;
    left: 0;
    top: 0;
    z-index: var(--z-modal);
    
    &:not(.collapsed) {
      box-shadow: 0 0 0 100vw rgba(0, 0, 0, 0.3);
    }
  }
}
</style>
