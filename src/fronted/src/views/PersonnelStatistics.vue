<template>
  <div class="personnel-statistics">
    <!-- 总体统计 -->
    <el-row :gutter="20" class="overview-stats">
      <el-col :span="8">
        <el-statistic title="总人数" :value="statistics.overview.total" />
      </el-col>
      <el-col :span="8">
        <el-statistic title="在职人员" :value="statistics.overview.active" />
      </el-col>
      <el-col :span="8">
        <el-statistic title="已卸任人员" :value="statistics.overview.inactive" />
      </el-col>
    </el-row>

    <el-divider />

    <!-- 按部门统计 -->
    <div class="department-stats">
      <h3>按部门统计</h3>
      <el-table :data="departmentStatsData" border style="width: 100%">
        <el-table-column prop="name" label="部门名称" />
        <el-table-column prop="total" label="总人数" align="center" />
        <el-table-column prop="active" label="在职" align="center">
          <template #default="scope">
            <el-tag type="success">{{ scope.row.active }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="inactive" label="已卸任" align="center">
          <template #default="scope">
            <el-tag type="danger">{{ scope.row.inactive }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="在职率" align="center">
          <template #default="scope">
            <el-progress
              :percentage="Math.round((scope.row.active / scope.row.total) * 100)"
              :color="getProgressColor(scope.row.active / scope.row.total)" />
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-divider />

    <!-- 按职位统计 -->
    <div class="position-stats">
      <h3>按职位统计</h3>
      <el-table :data="positionStatsData" border style="width: 100%">
        <el-table-column prop="name" label="职位名称" />
        <el-table-column prop="total" label="总人数" align="center" />
        <el-table-column prop="active" label="在职" align="center">
          <template #default="scope">
            <el-tag type="success">{{ scope.row.active }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="inactive" label="已卸任" align="center">
          <template #default="scope">
            <el-tag type="danger">{{ scope.row.inactive }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="stats-actions">
      <el-button @click="$emit('close')">关闭</el-button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PersonnelStatistics',
  props: {
    statistics: {
      type: Object,
      required: true
    }
  },
  emits: ['close'],
  computed: {
    departmentStatsData() {
      return Object.entries(this.statistics.by_department).map(([name, stats]) => ({
        name,
        ...stats
      }))
    },
    positionStatsData() {
      return Object.entries(this.statistics.by_position).map(([name, stats]) => ({
        name,
        ...stats
      }))
    }
  },
  methods: {
    getProgressColor(ratio) {
      if (ratio >= 0.8) return '#67c23a'
      if (ratio >= 0.6) return '#e6a23c'
      return '#f56c6c'
    }
  }
}
</script>

<style scoped>
.personnel-statistics {
  padding: 20px 0;
}

.overview-stats {
  margin-bottom: 30px;
}

.department-stats,
.position-stats {
  margin-bottom: 30px;
}

.department-stats h3,
.position-stats h3 {
  margin-bottom: 20px;
  color: #409eff;
}

.stats-actions {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}
</style>
