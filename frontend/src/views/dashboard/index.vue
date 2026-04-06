<template>
  <div class="professional-dashboard">
    <!-- 页面头部 -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon><DataLine /></el-icon>
          检验科工作台
        </h1>
        <p class="page-subtitle">实时监控与数据概览</p>
      </div>
      <div class="header-right">
        <div class="system-status">
          <el-tag :type="systemStatus.ok ? 'success' : 'danger'" size="small">
            <el-icon><CircleCheckFilled v-if="systemStatus.ok" /><CircleCloseFilled v-else /></el-icon>
            {{ systemStatus.text }}
          </el-tag>
          <span class="update-time">最后更新: {{ currentTime }}</span>
        </div>
        <el-button type="primary" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 核心指标卡片 -->
    <div class="metrics-grid">
      <el-card class="metric-card" shadow="hover">
        <div class="metric-header">
          <div class="metric-icon blue">
            <el-icon><Box /></el-icon>
          </div>
          <el-tag type="info" size="small">今日</el-tag>
        </div>
        <div class="metric-body">
          <div class="metric-value">{{ stats.todaySamples }}</div>
          <div class="metric-label">标本总数</div>
        </div>
        <div class="metric-footer">
          <span class="metric-change positive">
            <el-icon><Top /></el-icon>
            12%
          </span>
          <span class="metric-period">较昨日</span>
        </div>
      </el-card>

      <el-card class="metric-card" shadow="hover">
        <div class="metric-header">
          <div class="metric-icon green">
            <el-icon><Document /></el-icon>
          </div>
          <el-tag type="success" size="small">完成</el-tag>
        </div>
        <div class="metric-body">
          <div class="metric-value">{{ stats.completedReports }}</div>
          <div class="metric-label">已完成报告</div>
        </div>
        <div class="metric-footer">
          <span class="metric-change positive">
            <el-icon><Top /></el-icon>
            8%
          </span>
          <span class="metric-period">较昨日</span>
        </div>
      </el-card>

      <el-card class="metric-card" shadow="hover">
        <div class="metric-header">
          <div class="metric-icon orange">
            <el-icon><Clock /></el-icon>
          </div>
          <el-tag type="warning" size="small">待处理</el-tag>
        </div>
        <div class="metric-body">
          <div class="metric-value">{{ stats.pendingSamples }}</div>
          <div class="metric-label">待处理标本</div>
        </div>
        <div class="metric-footer">
          <span class="metric-change negative">
            <el-icon><Bottom /></el-icon>
            5%
          </span>
          <span class="metric-period">较昨日</span>
        </div>
      </el-card>

      <el-card class="metric-card" shadow="hover">
        <div class="metric-header">
          <div class="metric-icon red">
            <el-icon><WarningFilled /></el-icon>
          </div>
          <el-tag type="danger" size="small">危急</el-tag>
        </div>
        <div class="metric-body">
          <div class="metric-value">{{ stats.abnormalCount }}</div>
          <div class="metric-label">异常/危急值</div>
        </div>
        <div class="metric-footer">
          <span class="metric-change neutral">
            <el-icon><Minus /></el-icon>
            0%
          </span>
          <span class="metric-period">较昨日</span>
        </div>
      </el-card>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <!-- 标本状态分布 -->
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-title">
              <el-icon><PieChart /></el-icon>
              <span>标本状态分布</span>
            </div>
            <el-radio-group v-model="statusPeriod" size="small" @change="loadStatusChart">
              <el-radio-button label="today">今日</el-radio-button>
              <el-radio-button label="week">本周</el-radio-button>
              <el-radio-button label="month">本月</el-radio-button>
            </el-radio-group>
          </div>
        </template>
        <div ref="statusChartRef" class="chart-container"></div>
      </el-card>

      <!-- 检验趋势 -->
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-title">
              <el-icon><TrendCharts /></el-icon>
              <span>检验趋势</span>
            </div>
            <el-radio-group v-model="trendPeriod" size="small" @change="loadTrendChart">
              <el-radio-button label="7">近7天</el-radio-button>
              <el-radio-button label="30">近30天</el-radio-button>
            </el-radio-group>
          </div>
        </template>
        <div ref="trendChartRef" class="chart-container"></div>
      </el-card>
    </div>

    <!-- 底部工作区 -->
    <div class="bottom-section">
      <!-- 待办事项 -->
      <el-card class="todo-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-title">
              <el-icon><List /></el-icon>
              <span>待办事项</span>
              <el-badge :value="todoList.length" type="primary" />
            </div>
          </div>
        </template>
        <div class="todo-list">
          <div v-for="todo in todoList" :key="todo.id" class="todo-item" @click="handleTodoClick(todo)">
            <div class="todo-priority" :class="todo.priority">
              <el-icon v-if="todo.priority === 'high'"><Top /></el-icon>
              <el-icon v-else-if="todo.priority === 'medium'"><Right /></el-icon>
              <el-icon v-else><Bottom /></el-icon>
            </div>
            <div class="todo-content">
              <div class="todo-title">{{ todo.title }}</div>
              <div class="todo-meta">
                <el-tag size="small" :type="getTodoTypeTag(todo.type)">{{ todo.typeText }}</el-tag>
                <span class="todo-time">{{ todo.time }}</span>
              </div>
            </div>
            <div class="todo-action">
              <el-button size="small" type="primary" plain>处理</el-button>
            </div>
          </div>
          <el-empty v-if="todoList.length === 0" description="暂无待办事项" />
        </div>
      </el-card>

      <!-- 热门检验项目 -->
      <el-card class="hot-items-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-title">
              <el-icon><Histogram /></el-icon>
              <span>热门检验项目</span>
            </div>
          </div>
        </template>
        <div class="hot-items-list">
          <div v-for="(item, index) in hotTestItems" :key="item.id" class="hot-item">
            <div class="hot-rank" :class="getRankClass(index)">{{ index + 1 }}</div>
            <div class="hot-info">
              <div class="hot-name">{{ item.name }}</div>
              <div class="hot-count">{{ item.count }} 次</div>
            </div>
            <div class="hot-bar">
              <div class="hot-bar-fill" :style="{ width: item.percent + '%' }"></div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 最近操作日志 -->
      <el-card class="logs-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-title">
              <el-icon><Timer /></el-icon>
              <span>最近操作</span>
            </div>
            <el-button type="text" size="small" @click="viewAllLogs">查看全部</el-button>
          </div>
        </template>
        <div class="logs-list">
          <div v-for="log in recentLogs" :key="log.id" class="log-item">
            <div class="log-time">{{ log.time }}</div>
            <div class="log-type">
              <el-tag size="small" :type="getLogTypeTag(log.type)">{{ log.typeText }}</el-tag>
            </div>
            <div class="log-content">{{ log.content }}</div>
            <div class="log-operator">{{ log.operator }}</div>
          </div>
          <el-empty v-if="recentLogs.length === 0" description="暂无操作记录" />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  DataLine, Refresh, Box, Document, Clock, Warning,
  Check, Close, Top, Bottom, Minus,
  PieChart, TrendCharts, List, Histogram, Timer, Right,
  Odometer, Finished, Memo, Star,
  CircleCheckFilled, CircleCloseFilled
} from '@element-plus/icons-vue'
import { dashboardApi } from '@/api/dashboard'

const router = useRouter()

// 状态
const loading = ref(false)
const currentTime = ref('')
const statusPeriod = ref('today')
const trendPeriod = ref('7')

// 系统状态
const systemStatus = ref({
  ok: true,
  text: '系统正常'
})

// 统计数据
const stats = ref({
  todaySamples: 156,
  completedReports: 89,
  pendingSamples: 23,
  abnormalCount: 5
})

// 图表引用
const statusChartRef = ref(null)
const trendChartRef = ref(null)
let statusChart = null
let trendChart = null

// 待办事项
const todoList = ref([
  { id: 1, title: '审核检验报告 #RPT-2026032901', type: 'report', typeText: '报告审核', priority: 'high', time: '10分钟后' },
  { id: 2, title: '接收门诊标本 3份', type: 'sample', typeText: '标本接收', priority: 'medium', time: '30分钟后' },
  { id: 3, title: '复查异常结果', type: 'abnormal', typeText: '异常复查', priority: 'low', time: '今日内' }
])

// 热门检验项目
const hotTestItems = ref([
  { id: 1, name: '血常规检查', count: 456, percent: 100 },
  { id: 2, name: '肝功能检测', count: 312, percent: 68 },
  { id: 3, name: '肾功能检测', count: 287, percent: 63 },
  { id: 4, name: '血脂分析', count: 234, percent: 51 },
  { id: 5, name: '血糖检测', count: 198, percent: 43 }
])

// 最近操作日志
const recentLogs = ref([
  { id: 1, time: '10:30', type: 'sample', typeText: '标本', content: '签收门诊标本 #S2026032901', operator: '张三' },
  { id: 2, time: '10:25', type: 'report', typeText: '报告', content: '审核通过报告 #R2026032901', operator: '李四' },
  { id: 3, time: '10:20', type: 'test', typeText: '检验', content: '完成血常规检验', operator: '王五' },
  { id: 4, time: '10:15', type: 'patient', typeText: '患者', content: '患者王伟检验结果异常', operator: '系统' },
  { id: 5, time: '10:10', type: 'system', typeText: '系统', content: 'Redis缓存更新', operator: '系统' }
])

// 更新时间
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

// 刷新数据
const refreshData = async () => {
  loading.value = true
  try {
    // 并行加载所有数据
    const [statsResponse, todosResponse, hotItemsResponse, logsResponse] = await Promise.all([
      dashboardApi.getStats(),
      dashboardApi.getTodoList(),
      dashboardApi.getHotTestItems(),
      dashboardApi.getRecentLogs()
    ])

    // 更新统计数据
    if (statsResponse.data) {
      stats.value = {
        todaySamples: statsResponse.data.totalSamples || 0,
        completedReports: statsResponse.data.completedReports || 0,
        pendingSamples: statsResponse.data.pendingSamples || 0,
        abnormalCount: statsResponse.data.pendingReviews || 0
      }
    }

    // 更新待办事项
    if (todosResponse.data && Array.isArray(todosResponse.data)) {
      todoList.value = todosResponse.data
    }

    // 更新热门检验项目
    if (hotItemsResponse.data && Array.isArray(hotItemsResponse.data)) {
      hotTestItems.value = hotItemsResponse.data
    }

    // 更新操作日志
    if (logsResponse.data && Array.isArray(logsResponse.data)) {
      recentLogs.value = logsResponse.data
    }

    ElMessage.success('数据已刷新')
    updateTime()
    loadStatusChart()
    loadTrendChart()
  } catch (error) {
    console.error('刷新数据失败:', error)
    ElMessage.warning('刷新失败，使用缓存数据')
    // 如果API调用失败，保持当前数据不变（降级处理）
  } finally {
    loading.value = false
  }
}

// 加载状态图表
const loadStatusChart = () => {
  if (!statusChartRef.value) return
  
  statusChart = echarts.init(statusChartRef.value)
  const option = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 10, left: 'center' },
    color: ['#409EFF', '#67C23A', '#E6A23C', '#909399', '#F56C6C'],
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}\n{c}份' },
      data: [
        { value: 45, name: '待接收' },
        { value: 23, name: '检验中' },
        { value: 89, name: '已完成' },
        { value: 12, name: '异常' },
        { value: 5, name: '已归档' }
      ]
    }]
  }
  statusChart.setOption(option)
}

// 加载趋势图表
const loadTrendChart = () => {
  if (!trendChartRef.value) return
  
  trendChart = echarts.init(trendChartRef.value)
  const days = trendPeriod.value === '7' ? 7 : 30
  const labels = []
  const sampleData = []
  const reportData = []
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    labels.push(date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }))
    sampleData.push(Math.floor(Math.random() * 50) + 100)
    reportData.push(Math.floor(Math.random() * 40) + 80)
  }
  
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['标本数', '报告数'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
    xAxis: { type: 'category', data: labels, boundaryGap: false },
    yAxis: { type: 'value' },
    series: [
      {
        name: '标本数',
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.3 },
        data: sampleData,
        itemStyle: { color: '#409EFF' }
      },
      {
        name: '报告数',
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.3 },
        data: reportData,
        itemStyle: { color: '#67C23A' }
      }
    ]
  }
  trendChart.setOption(option)
}

// 处理待办点击
const handleTodoClick = (todo) => {
  if (todo.type === 'sample') {
    router.push('/sample')
  } else if (todo.type === 'report') {
    router.push('/report')
  }
}

// 查看全部日志
const viewAllLogs = () => {
  router.push('/system/logs')
}

// 获取排名样式
const getRankClass = (index) => {
  if (index === 0) return 'gold'
  if (index === 1) return 'silver'
  if (index === 2) return 'bronze'
  return ''
}

// 获取标签类型
const getTodoTypeTag = (type) => {
  const map = { report: 'primary', sample: 'success', abnormal: 'danger' }
  return map[type] || 'info'
}

const getLogTypeTag = (type) => {
  const map = { sample: 'primary', report: 'success', test: 'warning', patient: 'info', system: '' }
  return map[type] || 'info'
}

// 窗口调整
const handleResize = () => {
  statusChart?.resize()
  trendChart?.resize()
}

// 生命周期
onMounted(async () => {
  updateTime()
  setInterval(updateTime, 1000)

  // 初始加载所有数据
  await refreshData()

  // 加载图表
  loadStatusChart()
  loadTrendChart()

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  statusChart?.dispose()
  trendChart?.dispose()
})
</script>

<style scoped>
.professional-dashboard {
  padding: 0;
  background: transparent;
  min-height: 100%;
}

/* 页面头部 - 专业医疗设计 */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-lg) var(--spacing-xl);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%);
  border-radius: var(--border-radius-xl);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--primary-color) 0%, var(--medical-teal) 50%, var(--success-color) 100%);
  }
}

.page-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  letter-spacing: -0.5px;
  
  .el-icon {
    color: var(--primary-color);
  }
}

.page-subtitle {
  color: var(--text-tertiary);
  margin: var(--spacing-xs) 0 0 0;
  font-size: var(--font-size-sm);
}

.system-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-right: var(--spacing-md);
}

.update-time {
  font-size: var(--font-size-sm);
  color: var(--text-light);
}

/* 指标卡片网格 - 医疗系统专业设计 */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.metric-card {
  border-radius: var(--border-radius-xl) !important;
  border: 1px solid var(--border-light) !important;
  box-shadow: var(--shadow-sm) !important;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--primary-color), var(--primary-light));
    opacity: 0;
    transition: opacity 0.3s;
  }
  
  &:hover {
    transform: translateY(-6px);
    box-shadow: var(--shadow-lg) !important;
    border-color: var(--primary-bg) !important;
    
    &::before {
      opacity: 1;
    }
  }
  
  :deep(.el-card__body) {
    padding: var(--spacing-xl);
  }
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.metric-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--border-radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, transparent 60%);
  }
}

.metric-icon.blue { 
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%); 
}
.metric-icon.green { 
  background: linear-gradient(135deg, var(--success-color) 0%, var(--success-light) 100%); 
}
.metric-icon.orange { 
  background: linear-gradient(135deg, var(--warning-color) 0%, var(--warning-light) 100%); 
}
.metric-icon.red { 
  background: linear-gradient(135deg, var(--danger-color) 0%, var(--danger-light) 100%); 
}

.metric-body {
  margin-bottom: var(--spacing-md);
}

.metric-value {
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  line-height: 1;
  letter-spacing: -1px;
  margin-bottom: var(--spacing-xs);
}

.metric-label {
  font-size: var(--font-size-md);
  color: var(--text-tertiary);
  margin-top: var(--spacing-xs);
  font-weight: var(--font-weight-medium);
}

.metric-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--border-light);
}

.metric-change {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: var(--font-weight-semibold);
  padding: 4px 8px;
  border-radius: var(--border-radius-sm);
}

.metric-change.positive { 
  color: var(--success-color); 
  background-color: var(--success-bg);
}
.metric-change.negative { 
  color: var(--danger-color); 
  background-color: var(--danger-bg);
}
.metric-change.neutral { 
  color: var(--info-color); 
  background-color: var(--info-bg);
}

.metric-period {
  color: var(--text-light);
  font-weight: var(--font-weight-medium);
}

/* 图表区域 */
.charts-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.chart-card {
  border-radius: var(--border-radius-xl) !important;
  border: 1px solid var(--border-light) !important;
  box-shadow: var(--shadow-sm) !important;
  overflow: hidden;
  
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
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-lg);
  color: var(--text-primary);
  
  .el-icon {
    color: var(--primary-color);
  }
}

.chart-container {
  height: 300px;
}

/* 底部工作区 */
.bottom-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-lg);
}

.todo-card, .hot-items-card, .logs-card {
  border-radius: var(--border-radius-xl) !important;
  border: 1px solid var(--border-light) !important;
  box-shadow: var(--shadow-sm) !important;
  overflow: hidden;
  
  :deep(.el-card__header) {
    padding: var(--spacing-lg) var(--spacing-xl);
    border-bottom: 1px solid var(--border-light);
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%);
  }
  
  :deep(.el-card__body) {
    padding: var(--spacing-xl);
  }
}

/* 待办列表 */
.todo-list {
  max-height: 340px;
  overflow-y: auto;
  
  &::-webkit-scrollbar {
    width: 5px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 10px;
  }
}

.todo-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  margin-bottom: var(--spacing-sm);
  border: 1px solid transparent;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  &:hover {
    background: var(--bg-secondary);
    border-color: var(--primary-bg);
    transform: translateX(4px);
  }
}

.todo-priority {
  width: 28px;
  height: 28px;
  border-radius: var(--border-radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
  font-weight: var(--font-weight-semibold);
}

.todo-priority.high { 
  background: var(--danger-bg); 
  color: var(--danger-color); 
}
.todo-priority.medium { 
  background: var(--warning-bg); 
  color: var(--warning-color); 
}
.todo-priority.low { 
  background: var(--primary-bg); 
  color: var(--primary-color); 
}

.todo-content {
  flex: 1;
  min-width: 0;
}

.todo-title {
  font-size: var(--font-size-md);
  color: var(--text-primary);
  margin-bottom: var(--spacing-xs);
  font-weight: var(--font-weight-medium);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.todo-meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

.todo-time {
  font-size: var(--font-size-sm);
  color: var(--text-light);
  font-weight: var(--font-weight-medium);
}

/* 热门项目 */
.hot-items-list {
  max-height: 340px;
  overflow-y: auto;
  
  &::-webkit-scrollbar {
    width: 5px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 10px;
  }
}

.hot-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) 0;
  border-bottom: 1px solid var(--border-light);
  transition: all 0.2s;
  
  &:last-child {
    border-bottom: none;
  }
  
  &:hover {
    transform: translateX(4px);
    
    .hot-name {
      color: var(--primary-color);
    }
  }
}

.hot-rank {
  width: 32px;
  height: 32px;
  border-radius: var(--border-radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-md);
  background: var(--bg-secondary);
  color: var(--text-tertiary);
  flex-shrink: 0;
  transition: all 0.2s;
}

.hot-rank.gold { 
  background: linear-gradient(135deg, #ffd700 0%, #ffb700 100%); 
  color: white; 
  box-shadow: 0 4px 12px rgba(255, 183, 0, 0.35);
}
.hot-rank.silver { 
  background: linear-gradient(135deg, #c0c0c0 0%, #a0a0a0 100%); 
  color: white; 
  box-shadow: 0 4px 12px rgba(160, 160, 160, 0.3);
}
.hot-rank.bronze { 
  background: linear-gradient(135deg, #cd7f32 0%, #b87333 100%); 
  color: white; 
  box-shadow: 0 4px 12px rgba(184, 115, 51, 0.3);
}

.hot-info {
  flex: 1;
  min-width: 0;
}

.hot-name {
  font-size: var(--font-size-md);
  color: var(--text-primary);
  font-weight: var(--font-weight-medium);
  margin-bottom: 2px;
  transition: color 0.2s;
}

.hot-count {
  font-size: var(--font-size-sm);
  color: var(--text-light);
  font-weight: var(--font-weight-medium);
}

.hot-bar {
  width: 100px;
  height: 8px;
  background: var(--bg-secondary);
  border-radius: var(--border-radius-full);
  overflow: hidden;
  flex-shrink: 0;
}

.hot-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-color) 0%, var(--medical-teal) 50%, var(--success-color) 100%);
  border-radius: var(--border-radius-full);
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 操作日志 */
.logs-list {
  max-height: 340px;
  overflow-y: auto;
  
  &::-webkit-scrollbar {
    width: 5px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 10px;
  }
}

.log-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) 0;
  border-bottom: 1px solid var(--border-light);
  font-size: var(--font-size-sm);
  transition: all 0.2s;
  
  &:last-child {
    border-bottom: none;
  }
  
  &:hover {
    background: var(--bg-secondary);
    margin: 0 calc(-1 * var(--spacing-md));
    padding: var(--spacing-md);
    border-radius: var(--border-radius-md);
  }
}

.log-time {
  width: 55px;
  color: var(--text-light);
  font-weight: var(--font-weight-semibold);
  font-family: var(--font-family-mono);
  flex-shrink: 0;
}

.log-type {
  width: 65px;
  flex-shrink: 0;
}

.log-content {
  flex: 1;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: var(--font-weight-medium);
}

.log-operator {
  width: 55px;
  color: var(--primary-color);
  text-align: right;
  font-weight: var(--font-weight-semibold);
  flex-shrink: 0;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1200px) {
  .bottom-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }
}
</style>
