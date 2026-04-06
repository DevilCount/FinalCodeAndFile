import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Layout from '@/components/Layout.vue'
import { useUserStore } from '@/stores'
import { ElMessage } from 'element-plus'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 配置NProgress
NProgress.configure({ showSpinner: false, trickleSpeed: 200, minimum: 0.3 })

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import(/* webpackChunkName: "auth" */ '@/views/auth/Login.vue'),
    meta: { requiresAuth: false, title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import(/* webpackChunkName: "auth" */ '@/views/auth/Register.vue'),
    meta: { requiresAuth: false, title: '注册' }
  },
  {
    path: '/',
    component: Layout,
    meta: { requiresAuth: true },
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import(/* webpackChunkName: "dashboard" */ '@/views/dashboard/index.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: 'sample',
        name: 'Sample',
        component: () => import(/* webpackChunkName: "sample" */ '@/views/sample/index.vue'),
        meta: { title: '标本管理' }
      },
      {
        path: 'sample/create',
        name: 'SampleCreate',
        component: () => import(/* webpackChunkName: "sample" */ '@/views/sample/create.vue'),
        meta: { title: '创建标本' }
      },
      {
        path: 'sample/detail/:id',
        name: 'SampleDetail',
        component: () => import(/* webpackChunkName: "sample" */ '@/views/sample/detail.vue'),
        meta: { title: '标本详情' }
      },
      {
        path: 'report',
        name: 'Report',
        component: () => import(/* webpackChunkName: "report" */ '@/views/report/index.vue'),
        meta: { title: '报告管理' }
      },
      {
        path: 'report/create',
        name: 'ReportCreate',
        component: () => import(/* webpackChunkName: "report" */ '@/views/report/create.vue'),
        meta: { title: '创建报告' }
      },
      {
        path: 'report/detail/:id',
        name: 'ReportDetail',
        component: () => import(/* webpackChunkName: "report" */ '@/views/report/detail.vue'),
        meta: { title: '报告详情' }
      },
      {
        path: 'ai',
        name: 'AI',
        component: () => import(/* webpackChunkName: "ai" */ '@/views/ai/index.vue'),
        meta: { title: 'AI诊断' }
      },
      {
        path: 'user',
        name: 'User',
        component: () => import(/* webpackChunkName: "user" */ '@/views/user/index.vue'),
        meta: { title: '用户管理', roles: ['ADMIN'] }
      },
      {
        path: 'user/create',
        name: 'UserCreate',
        component: () => import(/* webpackChunkName: "user" */ '@/views/user/create.vue'),
        meta: { title: '创建用户', roles: ['ADMIN'] }
      },
      {
        path: 'user/edit/:id',
        name: 'UserEdit',
        component: () => import(/* webpackChunkName: "user" */ '@/views/user/edit.vue'),
        meta: { title: '编辑用户', roles: ['ADMIN'] }
      },
      {
        path: 'system',
        name: 'System',
        component: () => import(/* webpackChunkName: "system" */ '@/views/system/index.vue'),
        meta: { title: '系统设置', roles: ['ADMIN'] }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import(/* webpackChunkName: "error" */ '@/views/error/404.vue'),
    meta: { requiresAuth: false, title: '404 页面未找到' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 开始加载进度条
  NProgress.start()

  const userStore = useUserStore()

  // 设置页面标题
  const appTitle = import.meta.env.VITE_APP_TITLE || '实验室管理系统'
  document.title = to.meta.title ? `${to.meta.title} - ${appTitle}` : appTitle

  // 如果有token但没有用户信息，尝试从localStorage恢复
  if (userStore.token && !userStore.user) {
    try {
      await userStore.fetchUserInfo()
    } catch {
      NProgress.done()
      next({ name: 'Login' })
      return
    }
  }

  // 检查是否需要登录
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    NProgress.done()
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // 已登录用户访问登录页，跳转到首页
  if (to.name === 'Login' && userStore.isLoggedIn) {
    NProgress.done()
    next({ name: 'Dashboard' })
    return
  }

  // 检查角色权限
  if (to.meta.roles && Array.isArray(to.meta.roles)) {
    const hasRole = to.meta.roles.includes(userStore.userRole)
    if (!hasRole) {
      ElMessage.error('您没有权限访问该页面')
      NProgress.done()
      next({ name: from.name || 'Dashboard' })
      return
    }
  }

  next()
})

// 路由完成后关闭进度条
router.afterEach(() => {
  NProgress.done()
})

// 路由加载错误处理
router.onError((error) => {
  NProgress.done()
  console.error('路由加载错误:', error)
})

export default router
