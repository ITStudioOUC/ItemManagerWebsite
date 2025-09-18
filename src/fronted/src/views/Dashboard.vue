<template>
  <el-header>
    <div class="header-content">
      <h1 class="logo">爱特工作室物品管理系统</h1>
      <el-menu
          mode="horizontal"
          :default-active="$route.path"
          router
          class="nav-menu"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          首页
        </el-menu-item>
        <el-menu-item index="/items">
          <el-icon><Box /></el-icon>
          物品管理
        </el-menu-item>
        <el-menu-item index="/usage">
          <el-icon><Document /></el-icon>
          使用记录
        </el-menu-item>
      </el-menu>
    </div>
  </el-header>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon available">
              <el-icon><Box /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.available }}</h3>
              <p>可用物品</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon in-use">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.inUse }}</h3>
              <p>使用中</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon total">
              <el-icon><Grid /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.total }}</h3>
              <p>总物品数</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon maintenance">
              <el-icon><Tools /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.maintenance }}</h3>
              <p>维护中</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>当前使用中的物品</span>
          </template>
          <el-table :data="currentUsages" style="width: 100%" max-height="300">
            <el-table-column prop="item.name" label="物品名称" />
            <el-table-column prop="user.username" label="使用者" />
            <el-table-column prop="start_time" label="开始时间">
              <template #default="scope">
                {{ formatDate(scope.row.start_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="purpose" label="使用目的" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最新添加的物品</span>
          </template>
          <el-table :data="recentItems" style="width: 100%" max-height="300">
            <el-table-column prop="name" label="物品名称" />
            <el-table-column prop="category" label="类别" />
            <el-table-column prop="status" label="状态">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ getStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="添加时间">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { itemService, usageService } from '../services/api'
import moment from 'moment'

export default {
  name: 'Dashboard',
  data() {
    return {
      stats: {
        total: 0,
        available: 0,
        inUse: 0,
        maintenance: 0
      },
      currentUsages: [],
      recentItems: []
    }
  },
  async mounted() {
    await this.loadDashboardData()
  },
  methods: {
    async loadDashboardData() {
      try {
        // 获取统计数据
        const itemsResponse = await itemService.getAllItems()
        const items = itemsResponse.data

        this.stats.total = items.length
        this.stats.available = items.filter(item => item.status === 'available').length
        this.stats.inUse = items.filter(item => item.status === 'in_use').length
        this.stats.maintenance = items.filter(item => item.status === 'maintenance').length

        // 获取最新物品
        this.recentItems = items.slice(0, 5)

        // 获取当前使用记录
        const usagesResponse = await usageService.getCurrentUsages()
        this.currentUsages = usagesResponse.data.slice(0, 5)

      } catch (error) {
        console.error('加载仪表盘数据失败:', error)
        this.$message.error('加载数据失败')
      }
    },
    formatDate(dateString) {
      return moment(dateString).format('YYYY-MM-DD HH:mm')
    },
    getStatusType(status) {
      const typeMap = {
        'available': 'success',
        'in_use': 'warning',
        'maintenance': 'info',
        'damaged': 'danger'
      }
      return typeMap[status] || 'info'
    },
    getStatusText(status) {
      const textMap = {
        'available': '可用',
        'in_use': '使用中',
        'maintenance': '维护中',
        'damaged': '损坏'
      }
      return textMap[status] || '未知'
    }
  }
}
</script>

<style scoped>
.el-header {
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0,0,0,.12), 0 0 6px rgba(0,0,0,.04);
  height: 60px !important;
  display: flex;
  align-items: center;
  padding: 0 20px;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.logo {
  color: #409eff;
  font-size: 20px;
  font-weight: bold;
  margin: 0;
}

.nav-menu {
  border-bottom: none;
  background-color: transparent;
}

.nav-menu .el-menu-item {
  border-bottom: none;
  height: 60px;
  line-height: 60px;
}

.dashboard {
  padding: 20px;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 24px;
  color: white;
}

.stat-icon.available {
  background-color: #67c23a;
}

.stat-icon.in-use {
  background-color: #e6a23c;
}

.stat-icon.total {
  background-color: #409eff;
}

.stat-icon.maintenance {
  background-color: #909399;
}

.stat-info h3 {
  margin: 0;
  font-size: 28px;
  font-weight: bold;
}

.stat-info p {
  margin: 5px 0 0 0;
  color: #666;
}
</style>
