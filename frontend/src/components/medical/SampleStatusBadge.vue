<template>
  <div class="sample-status-badge" :class="[size, { interactive: interactive }]" @click="handleClick">
    <!-- 状态图标 -->
    <div class="status-icon" :class="status">
      <el-icon v-if="statusIcon">
        <component :is="statusIcon" />
      </el-icon>
    </div>
    
    <!-- 状态信息 -->
    <div class="status-info">
      <div class="status-text">
        <span class="status-name">{{ statusText }}</span>
        <el-tag v-if="showCount && sampleCount > 0" :type="statusType" size="small" class="count-badge">
          {{ sampleCount }}
        </el-tag>
      </div>
      <div v-if="description" class="status-desc">
        {{ description }}
      </div>
      <div v-if="timeInfo" class="time-info">
        <el-icon><Clock /></el-icon>
        <span>{{ timeInfo }}</span>
      </div>
    </div>
    
    <!-- 操作按钮 -->
    <div v-if="showAction && interactive" class="action-button">
      <el-button :type="actionType" size="small" @click.stop="handleAction">
        {{ actionText }}
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  Collection, Check, Search, Finished,
  Warning, Timer, Clock, ArrowRight
} from '@element-plus/icons-vue'

const props = defineProps({
  // 状态值
  status: {
    type: String,
    required: true,
    validator: (value) => [
      'pending',        // 待接收
      'received',       // 已接收
      'testing',        // 检验中
      'completed',      // 已完成
      'abnormal',       // 异常
      'archived',       // 已归档
      'transit',        // 运输中
      'rejected'        // 已拒收
    ].includes(value)
  },
  // 状态文本（可选，默认根据状态映射）
  statusText: {
    type: String,
    default: ''
  },
  // 状态描述
  description: {
    type: String,
    default: ''
  },
  // 时间信息
  timeInfo: {
    type: String,
    default: ''
  },
  // 标本数量
  sampleCount: {
    type: Number,
    default: 0
  },
  // 尺寸：small, medium, large
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  // 是否显示数量
  showCount: {
    type: Boolean,
    default: true
  },
  // 是否显示操作按钮
  showAction: {
    type: Boolean,
    default: false
  },
  // 操作按钮文本
  actionText: {
    type: String,
    default: '处理'
  },
  // 是否可交互
  interactive: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click', 'action'])

// 状态映射配置
const statusConfig = computed(() => {
  const config = {
    pending: {
      text: '待接收',
      icon: Collection,
      color: '#909399',
      bgColor: '#f4f4f5',
      borderColor: '#dcdfe6',
      type: 'info'
    },
    received: {
      text: '已接收',
      icon: Check,
      color: '#409eff',
      bgColor: '#ecf5ff',
      borderColor: '#b3d8ff',
      type: 'primary'
    },
    testing: {
      text: '检验中',
      icon: Search,
      color: '#e6a23c',
      bgColor: '#fdf6ec',
      borderColor: '#f5dab1',
      type: 'warning'
    },
    completed: {
      text: '已完成',
      icon: Finished,
      color: '#67c23a',
      bgColor: '#f0f9eb',
      borderColor: '#c2e7b0',
      type: 'success'
    },
    abnormal: {
      text: '异常',
      icon: Warning,
      color: '#f56c6c',
      bgColor: '#fef0f0',
      borderColor: '#fbc4c4',
      type: 'danger'
    },
    archived: {
      text: '已归档',
      icon: Timer,
      color: '#9e9e9e',
      bgColor: '#f5f5f5',
      borderColor: '#e0e0e0',
      type: 'info'
    },
    transit: {
      text: '运输中',
      icon: ArrowRight,
      color: '#8873e6',
      bgColor: '#f3f0ff',
      borderColor: '#d5ccff',
      type: 'primary'
    },
    rejected: {
      text: '已拒收',
      icon: Warning,
      color: '#ff5722',
      bgColor: '#fff3e0',
      borderColor: '#ffcc80',
      type: 'warning'
    }
  }
  
  return config[props.status] || config.pending
})

// 计算属性
const statusType = computed(() => statusConfig.value.type)
const statusIcon = computed(() => statusConfig.value.icon)
const finalStatusText = computed(() => props.statusText || statusConfig.value.text)
const actionType = computed(() => {
  // 根据状态决定操作按钮类型
  const map = {
    pending: 'success',
    received: 'primary',
    testing: 'warning',
    abnormal: 'danger',
    default: 'info'
  }
  return map[props.status] || map.default
})

// 方法
const handleClick = () => {
  if (props.interactive) {
    emit('click', props.status)
  }
}

const handleAction = () => {
  emit('action', props.status)
}
</script>

<style scoped>
.sample-status-badge {
  display: flex;
  align-items: center;
  padding: 16px;
  background-color: white;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  transition: all 0.3s ease;
  gap: 16px;
}

.sample-status-badge.interactive:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
  cursor: pointer;
  border-color: #409eff;
}

/* 尺寸样式 */
.sample-status-badge.small {
  padding: 8px 12px;
  gap: 8px;
}

.sample-status-badge.medium {
  padding: 16px;
  gap: 16px;
}

.sample-status-badge.large {
  padding: 20px;
  gap: 20px;
}

/* 状态图标 */
.status-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.small .status-icon {
  width: 32px;
  height: 32px;
  font-size: 16px;
}

.large .status-icon {
  width: 64px;
  height: 64px;
  font-size: 32px;
}

/* 状态颜色 */
.status-icon.pending {
  background-color: #f4f4f5;
  color: #909399;
}

.status-icon.received {
  background-color: #ecf5ff;
  color: #409eff;
}

.status-icon.testing {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.status-icon.completed {
  background-color: #f0f9eb;
  color: #67c23a;
}

.status-icon.abnormal {
  background-color: #fef0f0;
  color: #f56c6c;
}

.status-icon.archived {
  background-color: #f5f5f5;
  color: #9e9e9e;
}

.status-icon.transit {
  background-color: #f3f0ff;
  color: #8873e6;
}

.status-icon.rejected {
  background-color: #fff3e0;
  color: #ff5722;
}

/* 状态信息 */
.status-info {
  flex: 1;
  min-width: 0;
}

.status-text {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.status-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.small .status-name {
  font-size: 14px;
}

.large .status-name {
  font-size: 18px;
}

.count-badge {
  font-size: 12px;
  height: 20px;
  line-height: 18px;
  padding: 0 6px;
}

.status-desc {
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
  line-height: 1.4;
}

.small .status-desc {
  font-size: 12px;
}

.time-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.time-info .el-icon {
  font-size: 12px;
}

/* 操作按钮 */
.action-button {
  flex-shrink: 0;
}
</style>