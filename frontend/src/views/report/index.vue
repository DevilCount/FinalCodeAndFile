<template>
  <div class="professional-report-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon><Document /></el-icon>
          报告管理
        </h1>
        <p class="page-subtitle">检验报告审核与发布管理</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="goToCreate">
          <el-icon><Plus /></el-icon>
          新建报告
        </el-button>
      </div>
    </div>

    <!-- 报告统计 -->
    <div class="report-stats">
      <div class="stat-card">
        <div class="stat-icon pending">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ reportStats.pending }}</div>
          <div class="stat-label">待审核</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon reviewing">
          <el-icon><EditPen /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ reportStats.reviewing }}</div>
          <div class="stat-label">审核中</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon approved">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ reportStats.approved }}</div>
          <div class="stat-label">已通过</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon published">
          <el-icon><Finished /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ reportStats.published }}</div>
          <div class="stat-label">已发布</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon rejected">
          <el-icon><CloseBold /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ reportStats.rejected }}</div>
          <div class="stat-label">已驳回</div>
        </div>
      </div>
    </div>

    <!-- 筛选区域 -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-grid">
        <el-input
          v-model="searchKeyword"
          placeholder="报告编号、患者姓名、检验项目..."
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select v-model="filterStatus" placeholder="报告状态" clearable @change="handleSearch">
          <el-option label="待审核" value="PENDING" />
          <el-option label="技术审核中" value="TECHNICAL_REVIEW" />
          <el-option label="医师审核中" value="CLINICAL_REVIEW" />
          <el-option label="已发布" value="PUBLISHED" />
          <el-option label="已驳回" value="REJECTED" />
        </el-select>
        
        <el-select v-model="filterPriority" placeholder="优先级" clearable @change="handleSearch">
          <el-option label="紧急" value="HIGH" />
          <el-option label="普通" value="NORMAL" />
        </el-select>
        
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="handleSearch"
        />
      </div>
      
      <div class="filter-actions">
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="resetFilters">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
        <el-button type="success" @click="exportReports">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </el-card>

    <!-- 报告列表 -->
    <el-card class="report-list-card" shadow="hover">
      <el-table
        :data="reportList"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="reportNo" label="报告编号" width="180">
          <template #default="{ row }">
            <div class="report-no-cell">
              <el-icon class="report-icon"><Document /></el-icon>
              <span class="report-no-text">{{ row.reportNo }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="患者信息" width="200">
          <template #default="{ row }">
            <div class="patient-info">
              <div class="patient-name">
                <el-icon><User /></el-icon>
                {{ row.patientName }}
              </div>
              <div class="patient-meta">
                <span>ID: {{ row.patientId }}</span>
                <span>{{ row.patientAge }}岁</span>
                <span>{{ row.patientGender === 'M' ? '男' : '女' }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="sampleNo" label="关联标本" width="150">
          <template #default="{ row }">
            <el-tag size="small">{{ row.sampleNo }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="testItems" label="检验项目" min-width="180">
          <template #default="{ row }">
            <el-tag
              v-for="item in (row.testItems || '').split(',')"
              :key="item"
              size="small"
              style="margin-right: 4px; margin-bottom: 2px;"
            >
              {{ item.trim() }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="130">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" effect="light">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.priority === 'HIGH'" type="danger" size="small">
              <el-icon><Top /></el-icon> 紧急
            </el-tag>
            <el-tag v-else type="info" size="small">普通</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="审核进度" width="150">
          <template #default="{ row }">
            <div class="review-progress">
              <el-steps :space="40" :active="getReviewStep(row.status)" finish-status="success" size="small">
                <el-step title="技术" />
                <el-step title="医师" />
                <el-step title="发布" />
              </el-steps>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="createTime" label="创建时间" width="160">
          <template #default="{ row }">
            <span class="time-text">{{ formatDate(row.createTime) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" size="small" plain @click="viewReport(row)">
                <el-icon><View /></el-icon>
                查看
              </el-button>
              
              <el-dropdown @command="handleCommand($event, row)">
                <el-button type="primary" size="small">
                  更多 <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="review" v-if="canReview(row.status)">
                      <el-icon><EditPen /></el-icon> 审核
                    </el-dropdown-item>
                    <el-dropdown-item command="approve">
                      <el-icon><CircleCheck /></el-icon> 通过
                    </el-dropdown-item>
                    <el-dropdown-item command="reject">
                      <el-icon><CloseBold /></el-icon> 驳回
                    </el-dropdown-item>
                    <el-dropdown-item command="publish" v-if="row.status === 'APPROVED'">
                      <el-icon><Finished /></el-icon> 发布
                    </el-dropdown-item>
                    <el-dropdown-item command="print" divided>
                      <el-icon><Printer /></el-icon> 打印
                    </el-dropdown-item>
                    <el-dropdown-item command="export">
                      <el-icon><Download /></el-icon> 导出PDF
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </el-table-column>
        
        <template #empty>
          <el-empty description="暂无报告数据">
            <el-button type="primary" @click="goToCreate">新建报告</el-button>
          </el-empty>
        </template>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 审核对话框 -->
    <el-dialog
      v-model="reviewDialogVisible"
      :title="reviewDialogTitle"
      width="600px"
    >
      <el-form :model="reviewForm" label-width="100px">
        <el-form-item label="审核结果">
          <el-radio-group v-model="reviewForm.result">
            <el-radio label="approve">通过</el-radio>
            <el-radio label="reject">驳回</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审核意见">
          <el-input
            v-model="reviewForm.comment"
            type="textarea"
            :rows="4"
            placeholder="请输入审核意见..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReview">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document, Plus, Clock, EditPen, CircleCheck, Finished, CloseBold,
  Search, Refresh, Download, User, View, Top, ArrowDown, Printer
} from '@element-plus/icons-vue'
import { reportApi } from '@/api/report'
import { useUserStore } from '@/stores'

const router = useRouter()
const userStore = useUserStore()

// 状态
const loading = ref(false)
const searchKeyword = ref('')
const filterStatus = ref('')
const filterPriority = ref('')
const dateRange = ref([])
const reportList = ref([])

// 分页
const pagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

// 报告统计
const reportStats = reactive({
  pending: 8,
  reviewing: 5,
  approved: 12,
  published: 156,
  rejected: 3
})

// 审核对话框
const reviewDialogVisible = ref(false)
const reviewDialogTitle = ref('报告审核')
const reviewForm = reactive({
  result: 'approve',
  comment: ''
})
const currentReviewReport = ref(null)

// 状态映射
const statusMap = {
  PENDING: { text: '待审核', type: 'info' },
  TECHNICAL_REVIEW: { text: '技术审核中', type: 'warning' },
  CLINICAL_REVIEW: { text: '医师审核中', type: 'warning' },
  APPROVED: { text: '已通过', type: 'success' },
  PUBLISHED: { text: '已发布', type: 'success' },
  REJECTED: { text: '已驳回', type: 'danger' }
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    // 构建查询参数
    const params = {
      page: pagination.current,
      pageSize: pagination.size,
      keyword: searchKeyword.value,
      status: filterStatus.value,
      priority: filterPriority.value,
      startDate: dateRange.value?.[0],
      endDate: dateRange.value?.[1]
    }

    // 调用真实API获取数据
    const response = await reportApi.listReports(params)
    const result = response.data || {}

    reportList.value = result.list || result.records || []
    pagination.total = result.total || 0

    // 更新报告统计（从实际数据计算）
    updateReportStats()
  } catch (error) {
    console.error('加载报告列表失败:', error)
    ElMessage.error('加载数据失败，请检查网络连接')
    // 如果API调用失败，使用空数据但不阻断用户操作
    reportList.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

// 更新报告统计
const updateReportStats = () => {
  const stats = {
    pending: 0,
    reviewing: 0,
    approved: 0,
    published: 0,
    rejected: 0
  }

  reportList.value.forEach(report => {
    switch (report.status) {
      case 'PENDING':
        stats.pending++
        break
      case 'TECHNICAL_REVIEW':
      case 'CLINICAL_REVIEW':
        stats.reviewing++
        break
      case 'APPROVED':
      case 'REVIEWED':
        stats.approved++
        break
      case 'PUBLISHED':
        stats.published++
        break
      case 'REJECTED':
        stats.rejected++
        break
    }
  })

  // 更新响应式对象
  Object.assign(reportStats, stats)
}

// 搜索
const handleSearch = () => {
  pagination.current = 1
  loadData()
}

// 重置筛选
const resetFilters = () => {
  searchKeyword.value = ''
  filterStatus.value = ''
  filterPriority.value = ''
  dateRange.value = []
  handleSearch()
}

// 导出报告
const exportReports = () => {
  ElMessage.success('报告导出中...')
}

// 分页
const handleSizeChange = () => {
  loadData()
}

const handleCurrentChange = () => {
  loadData()
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取状态文本
const getStatusText = (status) => statusMap[status]?.text || status

// 获取状态标签类型
const getStatusTagType = (status) => statusMap[status]?.type || 'info'

// 获取审核步骤
const getReviewStep = (status) => {
  const steps = {
    PENDING: 0,
    TECHNICAL_REVIEW: 1,
    CLINICAL_REVIEW: 1,
    APPROVED: 2,
    PUBLISHED: 3,
    REJECTED: 0
  }
  return steps[status] || 0
}

// 判断是否可以审核
const canReview = (status) => {
  return ['PENDING', 'TECHNICAL_REVIEW', 'CLINICAL_REVIEW'].includes(status)
}

// 新建报告
const goToCreate = () => {
  router.push('/report/create')
}

// 查看报告
const viewReport = (row) => {
  router.push(`/report/detail/${row.id}`)
}

// 下拉菜单命令
const handleCommand = (command, row) => {
  currentReviewReport.value = row
  switch (command) {
    case 'review':
      reviewDialogTitle.value = '报告审核'
      reviewForm.result = 'approve'
      reviewForm.comment = ''
      reviewDialogVisible.value = true
      break
    case 'approve':
      approveReport(row)
      break
    case 'reject':
      rejectReport(row)
      break
    case 'publish':
      publishReport(row)
      break
    case 'print':
      printReport(row)
      break
    case 'export':
      exportReport(row)
      break
  }
}

// 通过报告
const approveReport = async (row) => {
  try {
    await ElMessageBox.confirm(`确定通过报告 ${row.reportNo} 吗？`, '通过确认')

    // 调用真实API审核报告
    await reportApi.reviewReport(row.id, {
      reviewerId: userStore.user?.id || 0,
      reviewerName: userStore.userName || '操作员',
      approved: true,
      remark: '审核通过'
    })

    ElMessage.success('报告已通过')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('通过报告失败:', error)
      ElMessage.error('操作失败，请重试')
    }
  }
}

// 驳回报告
const rejectReport = async (row) => {
  try {
    const { value: remark } = await ElMessageBox.prompt(
      `确定驳回报告 ${row.reportNo} 吗？请输入驳回原因：`,
      '驳回确认',
      {
        confirmButtonText: '确定驳回',
        cancelButtonText: '取消',
        inputPlaceholder: '请输入驳回原因',
        inputPattern: /\S+/,
        inputErrorMessage: '驳回原因不能为空',
        type: 'warning'
      }
    )

    // 调用真实API审核报告
    await reportApi.reviewReport(row.id, {
      reviewerId: userStore.user?.id || 0,
      reviewerName: userStore.userName || '操作员',
      approved: false,
      remark: remark
    })

    ElMessage.success('报告已驳回')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('驳回报告失败:', error)
      ElMessage.error('操作失败，请重试')
    }
  }
}

// 发布报告
const publishReport = async (row) => {
  try {
    await ElMessageBox.confirm(`确定发布报告 ${row.reportNo} 吗？发布后将不可修改！`, '发布确认', { type: 'warning' })

    // 调用真实API发布报告
    await reportApi.publishReport(row.id)

    ElMessage.success('报告已发布')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('发布报告失败:', error)
      ElMessage.error('操作失败，请重试')
    }
  }
}

// 打印报告
const printReport = (row) => {
  ElMessage.info(`正在打印报告 ${row.reportNo}...`)
}

// 导出单个报告
const exportReport = (row) => {
  ElMessage.success(`正在导出报告 ${row.reportNo}...`)
}

// 提交审核
const submitReview = async () => {
  if (!reviewForm.comment) {
    ElMessage.warning('请输入审核意见')
    return
  }

  if (!currentReviewReport.value) {
    ElMessage.warning('请先选择要审核的报告')
    return
  }

  try {
    // 调用真实API提交审核
    await reportApi.reviewReport(currentReviewReport.value.id, {
      reviewerId: userStore.user?.id || 0,
      reviewerName: userStore.userName || '操作员',
      approved: reviewForm.result === 'approve',
      remark: reviewForm.comment
    })

    ElMessage.success('审核提交成功')
    reviewDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('提交审核失败:', error)
    ElMessage.error('提交失败，请重试')
  }
}

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.professional-report-container {
  padding: 0;
  background: transparent;
  min-height: 100%;
}

/* 使用通用样式，针对特殊部分做微调 */
.report-icon {
  color: var(--primary-color);
}

.report-no-text {
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.review-progress {
  padding: var(--spacing-xs) 0;
}
</style>
