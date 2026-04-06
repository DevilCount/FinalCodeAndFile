<template>
  <div class="professional-system-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon><Setting /></el-icon>
          系统管理
        </h1>
        <p class="page-subtitle">系统配置与运维管理</p>
      </div>
    </div>

    <!-- 系统概览 -->
    <div class="system-overview">
      <el-card shadow="hover" class="overview-card">
        <div class="overview-grid">
          <div class="overview-item">
            <div class="overview-icon blue">
              <el-icon><Cpu /></el-icon>
            </div>
            <div class="overview-info">
              <div class="overview-value">7</div>
              <div class="overview-label">微服务数量</div>
            </div>
          </div>
          <div class="overview-item">
            <div class="overview-icon green">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="overview-info">
              <div class="overview-value">{{ serviceStatus.online }}</div>
              <div class="overview-label">在线服务</div>
            </div>
          </div>
          <div class="overview-item">
            <div class="overview-icon orange">
              <el-icon><User /></el-icon>
            </div>
            <div class="overview-info">
              <div class="overview-value">{{ onlineUsers }}</div>
              <div class="overview-label">在线用户</div>
            </div>
          </div>
          <div class="overview-item">
            <div class="overview-icon purple">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="overview-info">
              <div class="overview-value">{{ uptime }}</div>
              <div class="overview-label">运行时长</div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 服务状态 -->
    <el-card shadow="hover" class="services-card">
      <template #header>
        <div class="card-header">
          <el-icon><Box /></el-icon>
          <span>服务状态</span>
          <el-button type="primary" size="small" @click="refreshServices">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <el-table :data="services" stripe style="width: 100%">
        <el-table-column prop="name" label="服务名称" min-width="180">
          <template #default="{ row }">
            <div class="service-name">
              <el-icon><Box /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="port" label="端口" width="100" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'online' ? 'success' : 'danger'" size="small">
              {{ row.status === 'online' ? '在线' : '离线' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="health" label="健康检查" width="120">
          <template #default="{ row }">
            <el-tag :type="row.health === 'healthy' ? 'success' : 'warning'" size="small">
              {{ row.health === 'healthy' ? '健康' : '异常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button type="primary" size="small" plain @click="restartService(row)">
              <el-icon><Refresh /></el-icon>
              重启
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Redis缓存 -->
    <el-card shadow="hover" class="cache-card">
      <template #header>
        <div class="card-header">
          <el-icon><Histogram /></el-icon>
          <span>Redis缓存状态</span>
          <el-button type="success" size="small" @click="flushCache">
            <el-icon><Delete /></el-icon>
            清空缓存
          </el-button>
        </div>
      </template>
      <div class="cache-stats">
        <div class="cache-stat">
          <div class="stat-label">缓存键数量</div>
          <div class="stat-value">{{ cacheStats.keys }}</div>
        </div>
        <div class="cache-stat">
          <div class="stat-label">内存使用</div>
          <div class="stat-value">{{ cacheStats.memory }}</div>
        </div>
        <div class="cache-stat">
          <div class="stat-label">命中率</div>
          <div class="stat-value success">{{ cacheStats.hitRate }}%</div>
        </div>
        <div class="cache-stat">
          <div class="stat-label">连接数</div>
          <div class="stat-value">{{ cacheStats.connections }}</div>
        </div>
      </div>
    </el-card>

    <!-- 操作日志 -->
    <el-card shadow="hover" class="logs-card">
      <template #header>
        <div class="card-header">
          <el-icon><Timer /></el-icon>
          <span>最近操作日志</span>
          <el-button type="text" size="small" @click="viewAllLogs">查看全部</el-button>
        </div>
      </template>
      <el-table :data="recentLogs" stripe style="width: 100%">
        <el-table-column prop="time" label="时间" width="160" />
        <el-table-column prop="user" label="操作用户" width="120" />
        <el-table-column prop="module" label="模块" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.module }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="操作" />
        <el-table-column prop="ip" label="IP地址" width="140" />
        <el-table-column prop="result" label="结果" width="100">
          <template #default="{ row }">
            <el-tag :type="row.result === 'success' ? 'success' : 'danger'" size="small">
              {{ row.result === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Setting, Cpu, Connection, User, Clock, Box, Refresh,
  Histogram, Delete, Timer
} from '@element-plus/icons-vue'

const onlineUsers = ref(5)
const uptime = ref('3天 12小时')

const serviceStatus = reactive({
  online: 6,
  total: 7
})

const services = ref([
  { name: '用户服务 (lab-user-service)', port: 8086, status: 'online', health: 'healthy' },
  { name: '标本服务 (lab-sample-service)', port: 8082, status: 'online', health: 'healthy' },
  { name: '报告服务 (lab-report-service)', port: 8083, status: 'online', health: 'healthy' },
  { name: 'HL7服务 (lab-hl7-service)', port: 8084, status: 'online', health: 'healthy' },
  { name: 'AI服务 (lab-ai-service)', port: 8085, status: 'online', health: 'healthy' },
  { name: '网关服务 (lab-gateway)', port: 8080, status: 'online', health: 'healthy' },
  { name: '公共服务 (lab-common)', port: '-', status: 'online', health: 'healthy' }
])

const cacheStats = reactive({
  keys: 156,
  memory: '2.5MB',
  hitRate: 87.5,
  connections: 8
})

const recentLogs = ref([
  { time: '2026-03-29 15:30:00', user: 'admin', module: '用户管理', action: '登录系统', ip: '127.0.0.1', result: 'success' },
  { time: '2026-03-29 15:28:00', user: 'admin', module: '标本管理', action: '创建标本 #S2026032901', ip: '127.0.0.1', result: 'success' },
  { time: '2026-03-29 15:25:00', user: 'admin', module: '报告管理', action: '审核报告 #RPT2026032901', ip: '127.0.0.1', result: 'success' },
  { time: '2026-03-29 15:20:00', user: 'labtech1', module: '标本管理', action: '接收标本 #S2026032902', ip: '192.168.1.100', result: 'success' },
  { time: '2026-03-29 15:15:00', user: 'system', module: '系统', action: 'Redis缓存更新', ip: 'localhost', result: 'success' }
])

const refreshServices = () => {
  ElMessage.success('服务状态已刷新')
}

const restartService = (row) => {
  ElMessageBox.confirm(`确定重启服务 ${row.name} 吗？`, '重启确认', { type: 'warning' })
    .then(() => {
      ElMessage.success('服务重启中...')
    })
    .catch(() => {})
}

const flushCache = () => {
  ElMessageBox.confirm('确定清空所有缓存吗？这将导致系统性能暂时下降。', '清空缓存', { type: 'warning' })
    .then(() => {
      cacheStats.keys = 0
      ElMessage.success('缓存已清空')
    })
    .catch(() => {})
}

const viewAllLogs = () => {
  ElMessage.info('跳转到完整日志页面...')
}

onMounted(() => {})
</script>

<style scoped>
.professional-system-container {
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ed 100%);
  min-height: 100%;
}

.page-header {
  margin-bottom: 24px;
  padding: 20px 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-subtitle {
  color: #909399;
  margin: 4px 0 0;
  font-size: 14px;
}

.system-overview {
  margin-bottom: 20px;
}

.overview-card {
  border-radius: 12px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.overview-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 12px;
}

.overview-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
}

.overview-icon.blue { background: linear-gradient(135deg, #409EFF, #66b1ff); }
.overview-icon.green { background: linear-gradient(135deg, #67C23A, #85ce61); }
.overview-icon.orange { background: linear-gradient(135deg, #E6A23C, #ebb563); }
.overview-icon.purple { background: linear-gradient(135deg, #909399, #a6a9ad); }

.overview-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.overview-label {
  font-size: 13px;
  color: #909399;
}

.services-card, .cache-card, .logs-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.service-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.cache-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.cache-stat {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 12px;
  text-align: center;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.stat-value.success {
  color: #67C23A;
}

@media (max-width: 1200px) {
  .overview-grid, .cache-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .overview-grid, .cache-stats {
    grid-template-columns: 1fr;
  }
}
</style>
