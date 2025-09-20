<template>
  <el-card class="logout-card" shadow="never">
    <div class="logout-row">
      <div class="logout-info">
        <el-icon class="logout-icon"><User /></el-icon>
        <div class="logout-text">
          <div class="title">账户</div>
          <div class="desc">当前为已登录状态，如需切换账号请先退出登录</div>
        </div>
      </div>
      <div class="actions">
        <el-button type="danger" @click="logout" :loading="loading">
          退出登录
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script>
import { User } from '@element-plus/icons-vue'
import { authService } from '@/services/api'

export default {
  name: 'LogoutBar',
  components: { User },
  data() {
    return { loading: false }
  },
  methods: {
    async logout() {
      try {
        this.loading = true
        // 清除本地JWT
        authService.clearTokens()
        // 可选：清空本地与设置相关的缓存
        localStorage.removeItem('emailNotificationEnabled')
        // 跳转到登录页
        const redirect = this.$route.fullPath || '/'
        await this.$router.replace({ path: '/login', query: { redirect } })
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.logout-card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
  margin-bottom: 16px;
}

.logout-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.logout-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logout-icon {
  font-size: 22px;
  color: #409eff;
}

.logout-text .title {
  font-weight: 600;
  color: #303133;
}

.logout-text .desc {
  font-size: 12px;
  color: #909399;
}

@media (max-width: 768px) {
  .logout-row {
    flex-direction: column;
    align-items: flex-start;
  }
  .actions {
    width: 100%;
  }
  .actions .el-button {
    width: 100%;
  }
}
</style>

