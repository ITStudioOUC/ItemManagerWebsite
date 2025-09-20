<template>
  <AppHeader />
  <div class="item-usage">
    <div class="toolbar">
      <div class="filters">
        <el-select v-model="statusFilter" placeholder="状态筛选" @change="handleFilter">
          <el-option label="全部" value="" />
          <el-option label="使用中" value="false" />
          <el-option label="已归还" value="true" />
        </el-select>
        <el-select v-model="userFilter" placeholder="用户筛选" @change="handleFilter">
          <el-option label="全部用户" value="" />
          <el-option
            v-for="user in users"
            :key="user.id"
            :label="user.username"
            :value="user.id"
          />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="handleFilter"
        />
      </div>
    </div>

    <el-card>
      <el-table :data="filteredUsages" style="width: 100%" v-loading="loading">
        <el-table-column prop="item_name" label="物品名称" />
        <el-table-column prop="item_serial" label="序列号" />
        <el-table-column prop="user" label="使用者" />
        <el-table-column prop="start_time" label="开始时间" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="end_time" label="结束时间" width="160">
          <template #default="scope">
            {{ scope.row.end_time ? formatDate(scope.row.end_time) : '使用中' }}
          </template>
        </el-table-column>
        <el-table-column prop="purpose" label="使用目的" />
        <el-table-column prop="is_returned" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_returned ? 'success' : 'warning'">
              {{ scope.row.is_returned ? '已归还' : '使用中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="使用时长" width="120">
          <template #default="scope">
            {{ calculateDuration(scope.row) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button size="small" @click="showUsageDetail(scope.row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalUsages"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 使用记录详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="使用记录详情" width="700px">
      <div v-if="selectedUsage">
        <el-row :gutter="20">
          <el-col :span="12">
            <h3>物品信息</h3>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="物品名称">{{ selectedUsage.item_name }}</el-descriptions-item>
              <el-descriptions-item label="序列号">{{ selectedUsage.item_serial }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="12">
            <h3>使用者信息</h3>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="使用者">{{ selectedUsage.user }}</el-descriptions-item>
              <el-descriptions-item label="联系方式">{{ selectedUsage.borrower_contact }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>

        <h3 style="margin-top: 20px;">使用详情</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="使用目的">{{ selectedUsage.purpose }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDate(selectedUsage.start_time) }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ selectedUsage.end_time ? formatDate(selectedUsage.end_time) : '使用中' }}
          </el-descriptions-item>
          <el-descriptions-item label="使用时长">{{ calculateDuration(selectedUsage) }}</el-descriptions-item>
          <el-descriptions-item label="使用前状况">{{ selectedUsage.condition_before || '无记录' }}</el-descriptions-item>
          <el-descriptions-item label="使用后状况">{{ selectedUsage.condition_after || '无记录' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ selectedUsage.notes || '无' }}</el-descriptions-item>
          <el-descriptions-item label="状态" :span="2">
            <el-tag :type="selectedUsage.is_returned ? 'success' : 'warning'">
              {{ selectedUsage.is_returned ? '已归还' : '使用中' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 统计信息卡片 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="总使用记录" :value="totalUsages" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="当前使用中" :value="currentUsageCount" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="今日借用" :value="todayUsageCount" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="本月借用" :value="monthUsageCount" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { usageService, userService } from '@/services/api'
import { ElMessage } from 'element-plus'
import moment from 'moment'
import AppHeader from '../components/AppHeader.vue'

export default {
  name: 'ItemUsage',
  components: {
    AppHeader
  },
  data() {
    return {
      usages: [],
      users: [],
      loading: false,
      showDetailDialog: false,
      selectedUsage: null,
      statusFilter: '',
      userFilter: '',
      dateRange: null,
      currentPage: 1,
      pageSize: 20,
      totalUsages: 0,
      currentUsageCount: 0,
      todayUsageCount: 0,
      monthUsageCount: 0
    }
  },
  computed: {
    filteredUsages() {
      let filtered = this.usages

      // 状态筛选
      if (this.statusFilter !== '') {
        const isReturned = this.statusFilter === 'true'
        filtered = filtered.filter(usage => usage.is_returned === isReturned)
      }

      // 用户筛选
      if (this.userFilter) {
        filtered = filtered.filter(usage => usage.user.id === parseInt(this.userFilter))
      }

      // 日期范围筛选
      if (this.dateRange && this.dateRange.length === 2) {
        const startDate = moment(this.dateRange[0]).startOf('day')
        const endDate = moment(this.dateRange[1]).endOf('day')
        filtered = filtered.filter(usage => {
          const usageDate = moment(usage.start_time)
          return usageDate.isBetween(startDate, endDate, null, '[]')
        })
      }

      return filtered
    }
  },
  async mounted() {
    await this.loadData()
  },
  methods: {
    async loadData() {
      await Promise.all([
        this.loadUsages(),
        this.loadUsers(),
        this.loadStatistics()
      ])
    },
    async loadUsages() {
      this.loading = true
      try {
        const response = await usageService.getAllUsages()
        this.usages = response.data
        this.totalUsages = this.usages.length
      } catch (error) {
        console.error('加载使用记录失败:', error)
        ElMessage.error('加载使用记录失败')
      } finally {
        this.loading = false
      }
    },
    async loadUsers() {
      try {
        const response = await userService.getAllUsers()
        this.users = response.data
      } catch (error) {
        console.error('加载用户列表失败:', error)
      }
    },
    async loadStatistics() {
      try {
        // 计算统计数据
        const currentUsages = await usageService.getCurrentUsages()
        this.currentUsageCount = currentUsages.data.length

        const today = moment().startOf('day')
        const thisMonth = moment().startOf('month')

        this.todayUsageCount = this.usages.filter(usage =>
          moment(usage.start_time).isSameOrAfter(today)
        ).length

        this.monthUsageCount = this.usages.filter(usage =>
          moment(usage.start_time).isSameOrAfter(thisMonth)
        ).length
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    },
    handleFilter() {
      // 筛选逻辑在computed中处理
    },
    handleSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
    },
    handleCurrentChange(page) {
      this.currentPage = page
    },
    showUsageDetail(usage) {
      this.selectedUsage = usage
      this.showDetailDialog = true
    },
    formatDate(dateString) {
      return moment(dateString).format('YYYY-MM-DD HH:mm')
    },
    calculateDuration(usage) {
      const start = moment(usage.start_time)
      const end = usage.end_time ? moment(usage.end_time) : moment()
      const duration = moment.duration(end.diff(start))

      if (duration.asDays() >= 1) {
        return `${Math.floor(duration.asDays())}天${duration.hours()}小时`
      } else if (duration.asHours() >= 1) {
        return `${Math.floor(duration.asHours())}小时${duration.minutes()}分钟`
      } else {
        return `${Math.floor(duration.asMinutes())}分钟`
      }
    }
  }
}
</script>

<style scoped>
.item-usage {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-bottom: 20px;
}

.toolbar h2 {
  margin: 0;
}

.filters {
  display: flex;
  gap: 10px;
  align-items: center;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.stat-card {
  text-align: center;
}
</style>
