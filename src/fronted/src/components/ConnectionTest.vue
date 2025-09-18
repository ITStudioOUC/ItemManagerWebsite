/* eslint-disable */
<template>
  <div class="connection-test">
    <el-card>
      <template #header>
        <span>前后端连接测试</span>
      </template>
      <div v-if="loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        正在测试连接...
      </div>
      <div v-else>
        <el-result
          :icon="connectionStatus.success ? 'success' : 'error'"
          :title="connectionStatus.title"
          :sub-title="connectionStatus.message"
        >
          <template #extra>
            <el-button type="primary" @click="testConnection">重新测试</el-button>
          </template>
        </el-result>

        <div v-if="connectionStatus.success && apiData">
          <h3>API数据示例：</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="API状态">正常</el-descriptions-item>
            <el-descriptions-item label="响应时间">{{ responseTime }}ms</el-descriptions-item>
            <el-descriptions-item label="数据格式">JSON</el-descriptions-item>
            <el-descriptions-item label="CORS配置">已启用</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { healthService } from '../services/api'
import { ElMessage } from 'element-plus'

export default {
  name: 'ConnectionTest',
  data() {
    return {
      loading: false,
      connectionStatus: {
        success: false,
        title: '未测试',
        message: '点击测试按钮检查连接'
      },
      apiData: null,
      responseTime: 0
    }
  },
  async mounted() {
    await this.testConnection()
  },
  methods: {
    async testConnection() {
      this.loading = true
      const startTime = Date.now()

      try {
        const response = await healthService.checkBackendConnection()
        this.responseTime = Date.now() - startTime

        this.connectionStatus = {
          success: true,
          title: '连接成功！',
          message: '前后端连接正常，API可以正常访问'
        }

        this.apiData = response.data
        ElMessage.success('后端连接测试成功')

      } catch (error) {
        this.responseTime = Date.now() - startTime

        if (error.code === 'ERR_NETWORK') {
          this.connectionStatus = {
            success: false,
            title: '网络错误',
            message: '无法连接到后端服务器，请检查Django服务器是否运行在 http://localhost:8000'
          }
        } else if (error.response?.status === 404) {
          this.connectionStatus = {
            success: false,
            title: 'API路径错误',
            message: '后端服务器正在运行，但API路径配置有误'
          }
        } else {
          this.connectionStatus = {
            success: false,
            title: '连接失败',
            message: `错误: ${error.message}`
          }
        }

        console.error('连接测试失败:', error)
        ElMessage.error('后端连接测试失败')

      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.connection-test {
  padding: 20px;
}

.is-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
