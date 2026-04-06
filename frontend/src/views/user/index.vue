<template>
  <div class="professional-user-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon><User /></el-icon>
          用户管理
        </h1>
        <p class="page-subtitle">系统用户与权限管理</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="goToCreate">
          <el-icon><Plus /></el-icon>
          新建用户
        </el-button>
      </div>
    </div>

    <!-- 用户统计 -->
    <div class="user-stats">
      <div class="stat-card">
        <div class="stat-icon total">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ userStats.total }}</div>
          <div class="stat-label">总用户数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon admin">
          <el-icon><Key /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ userStats.admins }}</div>
          <div class="stat-label">管理员</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon doctor">
          <el-icon><UserFilled /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ userStats.doctors }}</div>
          <div class="stat-label">医生</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon tech">
          <el-icon><Monitor /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ userStats.technicians }}</div>
          <div class="stat-label">检验技师</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon online">
          <el-icon><Connection /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ userStats.online }}</div>
          <div class="stat-label">在线用户</div>
        </div>
      </div>
    </div>

    <!-- 筛选区域 -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-row">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索用户名、姓名、手机号..."
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select v-model="filterRole" placeholder="用户角色" clearable @change="handleSearch">
          <el-option label="管理员" value="ADMIN" />
          <el-option label="医生" value="DOCTOR" />
          <el-option label="检验技师" value="LAB_TECHNICIAN" />
          <el-option label="普通用户" value="USER" />
        </el-select>
        
        <el-select v-model="filterStatus" placeholder="用户状态" clearable @change="handleSearch">
          <el-option label="正常" value="1" />
          <el-option label="禁用" value="0" />
        </el-select>
        
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="resetFilters">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>
    </el-card>

    <!-- 用户列表 -->
    <el-card class="user-list-card" shadow="hover">
      <el-table
        :data="userList"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column label="用户信息" min-width="220">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="40" :icon="UserFilled" />
              <div class="user-info">
                <div class="user-name">
                  {{ row.realName || row.username }}
                  <el-tag v-if="row.role === 'ADMIN'" type="danger" size="small">管理员</el-tag>
                  <el-tag v-if="row.status === 1" type="success" size="small">正常</el-tag>
                  <el-tag v-else type="info" size="small">禁用</el-tag>
                </div>
                <div class="user-meta">
                  <span>@{{ row.username }}</span>
                  <span>{{ row.email || '未设置邮箱' }}</span>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="role" label="角色" width="140">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role)">
              {{ getRoleText(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="department" label="科室" width="150">
          <template #default="{ row }">
            <span class="department-text">{{ row.department || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="phone" label="手机号" width="130">
          <template #default="{ row }">
            <span class="phone-text">{{ row.phone || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="createTime" label="创建时间" width="160">
          <template #default="{ row }">
            <span class="time-text">{{ formatDate(row.createTime) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="最后登录" width="160">
          <template #default="{ row }">
            <span class="time-text">{{ row.lastLoginTime || '从未登录' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" size="small" plain @click="editUser(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button
                :type="row.status === 1 ? 'warning' : 'success'"
                size="small"
                plain
                @click="toggleStatus(row)"
              >
                <el-icon v-if="row.status === 1"><Lock /></el-icon>
                <el-icon v-else><Unlock /></el-icon>
                {{ row.status === 1 ? '禁用' : '启用' }}
              </el-button>
              <el-dropdown @command="handleCommand($event, row)">
                <el-button type="primary" size="small">
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="resetPwd">
                      <el-icon><Key /></el-icon> 重置密码
                    </el-dropdown-item>
                    <el-dropdown-item command="viewLogs">
                      <el-icon><Timer /></el-icon> 操作日志
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" divided>
                      <el-icon><Delete /></el-icon> 删除用户
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </el-table-column>
        
        <template #empty>
          <el-empty description="暂无用户数据">
            <el-button type="primary" @click="goToCreate">新建用户</el-button>
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

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="editDialogTitle"
      width="600px"
    >
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" :disabled="isEditMode" />
        </el-form-item>
        <el-form-item label="真实姓名">
          <el-input v-model="editForm.realName" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="editForm.role" style="width: 100%">
            <el-option label="管理员" value="ADMIN" />
            <el-option label="医生" value="DOCTOR" />
            <el-option label="检验技师" value="LAB_TECHNICIAN" />
            <el-option label="普通用户" value="USER" />
          </el-select>
        </el-form-item>
        <el-form-item label="科室">
          <el-input v-model="editForm.department" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="editForm.phone" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="editForm.status" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User, Plus, Key, UserFilled, Monitor, Connection,
  Search, Refresh, Edit, Lock, Unlock, Delete,
  ArrowDown, Timer
} from '@element-plus/icons-vue'
import userService from '../../services/userService'

const router = useRouter()

// 状态
const loading = ref(false)
const searchKeyword = ref('')
const filterRole = ref('')
const filterStatus = ref('')
const userList = ref([])

// 分页
const pagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

// 用户统计
const userStats = reactive({
  total: 24,
  admins: 3,
  doctors: 8,
  technicians: 10,
  online: 5
})

// 编辑对话框
const editDialogVisible = ref(false)
const editDialogTitle = ref('新建用户')
const isEditMode = ref(false)
const editForm = reactive({
  id: null,
  username: '',
  realName: '',
  role: 'USER',
  department: '',
  phone: '',
  email: '',
  status: 1
})

// 角色映射
const roleMap = {
  ADMIN: { text: '管理员', type: 'danger' },
  DOCTOR: { text: '医生', type: 'primary' },
  LAB_TECHNICIAN: { text: '检验技师', type: 'success' },
  USER: { text: '普通用户', type: 'info' }
}

// 获取角色文本
const getRoleText = (role) => roleMap[role]?.text || role

// 获取角色标签类型
const getRoleTagType = (role) => roleMap[role]?.type || 'info'

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    // 模拟数据
    userList.value = [
      { id: 1, username: 'admin', realName: '系统管理员', role: 'ADMIN', department: '信息中心', phone: '13800000001', email: 'admin@lab.com', status: 1, createTime: '2026-01-01 08:00:00', lastLoginTime: '2026-03-29 10:30:00' },
      { id: 2, username: 'doctor1', realName: '张医生', role: 'DOCTOR', department: '内科', phone: '13800000002', email: 'doctor1@lab.com', status: 1, createTime: '2026-01-15 09:00:00', lastLoginTime: '2026-03-29 09:15:00' },
      { id: 3, username: 'labtech1', realName: '李技师', role: 'LAB_TECHNICIAN', department: '检验科', phone: '13800000003', email: 'labtech1@lab.com', status: 1, createTime: '2026-02-01 10:00:00', lastLoginTime: '2026-03-29 08:30:00' },
      { id: 4, username: 'testuser', realName: '测试用户', role: 'USER', department: '', phone: '13800138000', email: 'test@example.com', status: 1, createTime: '2026-03-20 14:00:00', lastLoginTime: null }
    ]
    pagination.total = userList.value.length
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.current = 1
  loadData()
}

// 重置筛选
const resetFilters = () => {
  searchKeyword.value = ''
  filterRole.value = ''
  filterStatus.value = ''
  handleSearch()
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

// 新建用户
const goToCreate = () => {
  router.push('/user/create')
}

// 编辑用户
const editUser = (row) => {
  isEditMode.value = true
  editDialogTitle.value = '编辑用户'
  editForm.id = row.id
  editForm.username = row.username
  editForm.realName = row.realName
  editForm.role = row.role
  editForm.department = row.department
  editForm.phone = row.phone
  editForm.email = row.email
  editForm.status = row.status
  editDialogVisible.value = true
}

// 提交编辑
const submitEdit = async () => {
  if (!editForm.username || !editForm.realName) {
    ElMessage.warning('请填写完整信息')
    return
  }
  ElMessage.success('保存成功')
  editDialogVisible.value = false
  loadData()
}

// 切换状态
const toggleStatus = async (row) => {
  const action = row.status === 1 ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确定${action}用户 ${row.username} 吗？`, `${action}确认`)
    ElMessage.success(`${action}成功`)
    loadData()
  } catch {
    // 取消
  }
}

// 下拉菜单命令
const handleCommand = (command, row) => {
  switch (command) {
    case 'resetPwd':
      resetPassword(row)
      break
    case 'viewLogs':
      viewLogs(row)
      break
    case 'delete':
      deleteUser(row)
      break
  }
}

// 重置密码
const resetPassword = async (row) => {
  try {
    await ElMessageBox.confirm(`确定重置用户 ${row.username} 的密码吗？`, '重置密码', { type: 'warning' })
    ElMessage.success('密码已重置为默认密码: 123456')
  } catch {
    // 取消
  }
}

// 查看日志
const viewLogs = (row) => {
  router.push(`/system/logs?userId=${row.id}`)
}

// 删除用户
const deleteUser = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除用户 ${row.username} 吗？此操作不可恢复！`, '删除确认', { type: 'error' })
    ElMessage.success('删除成功')
    loadData()
  } catch {
    // 取消
  }
}

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.professional-user-container {
  padding: 0;
  background: transparent;
  min-height: 100%;
}

/* 使用通用样式，针对特殊部分做微调 */
</style>
