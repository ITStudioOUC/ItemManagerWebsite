<template>
  <AppHeader />
  <div class="dashboard">
    <el-row :gutter="42">
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
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon damaged">
              <el-icon><WarningFilled /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.damaged }}</h3>
              <p>损坏</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon lost">
              <el-icon><QuestionFilled /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.lost }}</h3>
              <p>丢失</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon abandoned">
              <el-icon><Delete /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.abandoned }}</h3>
              <p>已弃用</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon prohibited">
              <el-icon><Lock /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.prohibited }}</h3>
              <p>禁止借用</p>
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
            <el-table-column prop="item_name" label="物品名称" />
            <el-table-column prop="user" label="使用者" />
            <el-table-column prop="start_time" label="开始时间">
              <template #default="scope">
                {{ formatDate(scope.row.start_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="purpose" label="使用目的">
              <template #default="scope">
                {{ scope.row.purpose || '无' }}
              </template>
            </el-table-column>
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
import AppHeader from '../components/AppHeader.vue'

export default {
  name: 'Dashboard',
  components: {
    AppHeader
  },
  data() {
    return {
      stats: {
        total: 0,
        available: 0,
        inUse: 0,
        maintenance: 0,
        damaged: 0,
        lost: 0,
        abandoned: 0,
        prohibited: 0,
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
        this.stats.damaged = items.filter(item => item.status === 'damaged').length
        this.stats.lost = items.filter(item => item.status === 'lost').length
        this.stats.abandoned = items.filter(item => item.status === 'abandoned').length
        this.stats.prohibited = items.filter(item => item.status === 'prohibited').length

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
        'damaged': 'danger',
        'lost': 'danger',
        'abandoned': 'info',
        'prohibited': 'warning',
      }
      return typeMap[status] || 'info'
    },
    getStatusText(status) {
      const textMap = {
        'available': '可用',
        'in_use': '使用中',
        'maintenance': '维护中',
        'damaged': '损坏',
        'lost': '丢失',
        'abandoned': '已弃用',
        'prohibited': '禁止借用',
      }
      return textMap[status] || '未知'
    }
  }
}
</script>

<style scoped>
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

.stat-icon.damaged {
  background-color: #f56c6c;
}

.stat-icon.lost {
  background-color: #f59e0b;
}

.stat-icon.abandoned {
  background-color: #8e8e8e;
}

.stat-icon.prohibited {
  background-color: #409eff;
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
