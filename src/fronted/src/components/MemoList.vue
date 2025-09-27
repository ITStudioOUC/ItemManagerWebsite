<template>
  <div class="memo-list">
    <div class="memo-list-header">
      <div class="search-bar">
        <el-input
          v-model="localSearchText"
          placeholder="搜索备忘录..."
          prefix-icon="Search"
          @input="handleSearchInput"
          clearable
        />
      </div>
      <el-button
        type="primary"
        @click="$emit('create')"
        class="create-btn"
        :icon="Plus"
      >
        新建
      </el-button>
    </div>

    <div class="memo-list-content">
      <el-loading v-if="loading" class="loading-container" text="加载中..." />

      <div v-else-if="memos.length === 0" class="empty-state">
        <el-empty description="暂无备忘录" />
      </div>

      <div v-else class="memo-items">
        <div
          v-for="memo in memos"
          :key="memo.id"
          class="memo-item"
          :class="{ active: selectedMemoId === memo.id }"
          @click="$emit('select', memo)"
        >
          <div class="memo-item-header">
            <h3 class="memo-title">{{ memo.title || '无标题' }}</h3>
            <el-dropdown trigger="click" @command="(command) => handleCommand(command, memo)">
              <el-button text size="small" class="more-btn">
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="delete" class="delete-item">
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>

          <p class="memo-preview">{{ memo.content_preview || '无内容' }}</p>

          <div class="memo-meta">
            <span class="memo-author">{{ memo.created_by_name }}</span>
            <span class="memo-date">{{ formatDate(memo.updated_at) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { Plus, MoreFilled, Delete } from '@element-plus/icons-vue'

export default {
  name: 'MemoList',
  props: {
    memos: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    searchText: {
      type: String,
      default: ''
    },
    selectedMemoId: {
      type: [Number, String],
      default: null
    }
  },
  emits: ['search', 'select', 'create', 'delete'],
  setup(props, { emit }) {
    const localSearchText = ref(props.searchText)
    let searchTimeout = null

    const handleSearchInput = () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        emit('search', localSearchText.value)
      }, 300)
    }

    const handleCommand = async (command, memo) => {
      if (command === 'delete') {
        try {
          await ElMessageBox.confirm(
            `确定要删除备忘录 "${memo.title}" 吗？`,
            '确认删除',
            {
              confirmButtonText: '确定',
              cancelButtonText: '取消',
              type: 'warning'
            }
          )
          emit('delete', memo.id)
        } catch {
          // 用户取消删除
        }
      }
    }

    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      const now = new Date()
      const diff = now - date

      // 如果是今天
      if (diff < 24 * 60 * 60 * 1000 && now.getDate() === date.getDate()) {
        return date.toLocaleTimeString('zh-CN', {
          hour: '2-digit',
          minute: '2-digit'
        })
      }

      // 如果是今年
      if (now.getFullYear() === date.getFullYear()) {
        return date.toLocaleDateString('zh-CN', {
          month: 'short',
          day: 'numeric'
        })
      }

      // 其他情况显示完整日期
      return date.toLocaleDateString('zh-CN')
    }

    watch(() => props.searchText, (newVal) => {
      localSearchText.value = newVal
    })

    return {
      localSearchText,
      handleSearchInput,
      handleCommand,
      formatDate,
      Plus,
      MoreFilled,
      Delete
    }
  }
}
</script>

<style scoped>
.memo-list {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.memo-list-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  background-color: #fafafa;
}

.search-bar {
  margin-bottom: 12px;
}

.create-btn {
  width: 100%;
}

.memo-list-content {
  flex: 1;
  overflow-y: auto;
}

.loading-container {
  height: 200px;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
}

.memo-items {
  padding: 0;
}

.memo-item {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;
}

.memo-item:hover {
  background-color: #f8f9fa;
}

.memo-item.active {
  background-color: #e8f4fd;
  border-left: 3px solid #409eff;
}

.memo-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.memo-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  flex: 1;
  padding-right: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.more-btn {
  opacity: 0;
  transition: opacity 0.2s;
  color: #909399;
  padding: 4px;
}

.memo-item:hover .more-btn {
  opacity: 1;
}

.memo-preview {
  font-size: 12px;
  color: #606266;
  line-height: 1.4;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.memo-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #909399;
}

.memo-author {
  font-weight: 500;
}

.memo-date {
  font-variant-numeric: tabular-nums;
}

.delete-item {
  color: #f56c6c;
}

/* 滚动条样式 */
.memo-list-content::-webkit-scrollbar {
  width: 6px;
}

.memo-list-content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.memo-list-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.memo-list-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>