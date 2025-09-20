<template>
  <div>
    <AppHeader />
    <div class="personnel-container">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>人员管理</span>
            <el-button type="primary" @click="showAddDialog">
              <el-icon><Plus /></el-icon>
              添加人员
            </el-button>
          </div>
        </template>

        <!-- 搜索和筛选区域 -->
        <div class="filter-section">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索姓名、学号、手机号"
                clearable
                @input="handleSearch">
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-col>
            <el-col :span="4">
              <el-select v-model="departmentFilter" placeholder="部门筛选" clearable @change="handleFilter">
                <el-option label="全部部门" value="" />
                <el-option
                  v-for="dept in departments"
                  :key="dept.id"
                  :label="dept.name"
                  :value="dept.id" />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-select v-model="projectGroupFilter" placeholder="项目组筛选" clearable @change="handleFilter">
                <el-option label="全部项目组" value="" />
                <el-option
                  v-for="group in projectGroups"
                  :key="group.id"
                  :label="group.name"
                  :value="group.id" />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-input
                v-model="positionFilter"
                placeholder="职位搜索"
                clearable
                @input="handleFilter">
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-col>
            <el-col :span="3">
              <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="handleFilter">
                <el-option label="全部状态" value="" />
                <el-option label="在职" value="true" />
                <el-option label="已卸任" value="false" />
              </el-select>
            </el-col>
            <el-col :span="3">
              <el-button @click="showStatistics" type="success">
                <el-icon><DataAnalysis /></el-icon>
                统计信息
              </el-button>
            </el-col>
          </el-row>
        </div>

        <!-- 人员列表表格 -->
        <el-table :data="paginatedPersonnel" style="width: 100%" v-loading="loading">
          <el-table-column prop="name" label="姓名" width="100" />
          <el-table-column prop="student_id" label="学号" width="120" />
          <el-table-column prop="gender_display" label="性别" width="80" />
          <el-table-column prop="grade_major" label="年级专业" min-width="150" />
          <el-table-column prop="department_name" label="部门" width="120" />
          <el-table-column prop="project_group_name" label="项目组" width="120">
            <template #default="scope">
              {{ scope.row.project_group_name || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="position" label="职位" width="100" />
          <el-table-column prop="is_active" label="状态" width="80">
            <template #default="scope">
              <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
                {{ scope.row.is_active ? '在职' : '已卸任' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="phone" label="手机号" width="120" />
          <el-table-column prop="start_date" label="任职开始" width="110" />
          <el-table-column label="操作" width="300" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="viewDetail(scope.row)">详情</el-button>
              <el-button size="small" @click="editPersonnel(scope.row)">编辑</el-button>
              <el-button
                v-if="scope.row.is_active"
                size="small"
                type="warning"
                @click="setInactive(scope.row.id)">
                设为已卸任
              </el-button>
              <el-button
                v-else
                size="small"
                type="success"
                @click="setActive(scope.row.id)">
                设为在职
              </el-button>
              <el-button size="small" type="danger" @click="deletePersonnel(scope.row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页组件 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="filteredPersonnel.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange">
          </el-pagination>
        </div>
      </el-card>

      <!-- 添加/编辑人员对话框 -->
      <el-dialog :title="dialogTitle" v-model="dialogVisible" width="60%">
        <PersonnelForm
          :personnel="selectedPersonnel"
          :departments="departments"
          :project-groups="projectGroups"
          @submit="handleFormSubmit"
          @cancel="dialogVisible = false"
        />
      </el-dialog>

      <!-- 人员详情对话框 -->
      <el-dialog title="人员详情" v-model="detailDialogVisible" width="50%">
        <PersonnelDetail
          v-if="selectedPersonnel"
          :personnel="selectedPersonnel"
          @close="detailDialogVisible = false"
        />
      </el-dialog>

      <!-- 统计信息对话框 -->
      <el-dialog title="人员统计信息" v-model="statisticsDialogVisible" width="70%">
        <PersonnelStatistics
          v-if="statistics"
          :statistics="statistics"
          @close="statisticsDialogVisible = false"
        />
      </el-dialog>
    </div>
  </div>
</template>

<script>
import {financeService, personnelService, projectGroupService} from '@/services/api'
import AppHeader from '@/components/AppHeader.vue'
import PersonnelForm from './PersonnelForm.vue'
import PersonnelDetail from './PersonnelDetail.vue'
import PersonnelStatistics from './PersonnelStatistics.vue'
import {DataAnalysis, Plus, Search} from '@element-plus/icons-vue'

export default {
  name: 'PersonnelList',
  components: {
    AppHeader,
    PersonnelForm,
    PersonnelDetail,
    PersonnelStatistics,
    Search,
    Plus,
    DataAnalysis
  },
  data() {
    return {
      personnel: [],
      departments: [],
      projectGroups: [],
      statistics: null,
      loading: false,

      // 搜索和筛选
      searchKeyword: '',
      departmentFilter: '',
      projectGroupFilter: '',
      positionFilter: '',
      statusFilter: '',

      // 分页
      currentPage: 1,
      pageSize: 20,

      // 对话框
      dialogVisible: false,
      detailDialogVisible: false,
      statisticsDialogVisible: false,
      dialogTitle: '',
      selectedPersonnel: null
    }
  },
  computed: {
    filteredPersonnel() {
      let filtered = [...this.personnel]

      // 搜索过滤
      if (this.searchKeyword) {
        const keyword = this.searchKeyword.toLowerCase()
        filtered = filtered.filter(person =>
          person.name.toLowerCase().includes(keyword) ||
          person.student_id.includes(keyword) ||
          person.phone.includes(keyword) ||
          person.email.toLowerCase().includes(keyword)
        )
      }

      // 部门筛选
      if (this.departmentFilter) {
        filtered = filtered.filter(person => person.department === parseInt(this.departmentFilter))
      }

      // 项目组筛选
      if (this.projectGroupFilter) {
        filtered = filtered.filter(person => person.project_group === parseInt(this.projectGroupFilter))
      }

      // 职位筛选
      if (this.positionFilter) {
        const positionKeyword = this.positionFilter.toLowerCase()
        filtered = filtered.filter(person =>
          person.position && person.position.toLowerCase().includes(positionKeyword)
        )
      }

      // 状态筛选
      if (this.statusFilter !== '') {
        filtered = filtered.filter(person => person.is_active === (this.statusFilter === 'true'))
      }

      return filtered
    },
    paginatedPersonnel() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.filteredPersonnel.slice(start, end)
    }
  },
  async created() {
    await this.loadData()
  },
  methods: {
    async loadData() {
      await Promise.all([
        this.fetchPersonnel(),
        this.fetchDepartments(),
        this.fetchProjectGroups()
      ])
    },

    async fetchPersonnel() {
      this.loading = true
      try {
        const response = await personnelService.getAllPersonnel()
        this.personnel = response.data
      } catch (error) {
        this.$message.error('获取人员列表失败')
        console.error('获取人员列表失败:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchDepartments() {
      try {
        const response = await financeService.getAllDepartments()
        this.departments = response.data
      } catch (error) {
        console.error('获取部门列表失败:', error)
      }
    },

    async fetchProjectGroups() {
      try {
        const response = await projectGroupService.getAllProjectGroups()
        this.projectGroups = response.data
      } catch (error) {
        console.error('获取项目组列表失败:', error)
      }
    },

    handleSearch() {
      this.currentPage = 1
    },

    handleFilter() {
      this.currentPage = 1
    },

    handleSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
    },

    handleCurrentChange(page) {
      this.currentPage = page
    },

    showAddDialog() {
      this.selectedPersonnel = null
      this.dialogTitle = '添加人员'
      this.dialogVisible = true
    },

    editPersonnel(personnel) {
      this.selectedPersonnel = { ...personnel }
      this.dialogTitle = '编辑人员'
      this.dialogVisible = true
    },

    viewDetail(personnel) {
      this.selectedPersonnel = personnel
      this.detailDialogVisible = true
    },

    async showStatistics() {
      try {
        const response = await personnelService.getPersonnelStatistics()
        this.statistics = response.data
        this.statisticsDialogVisible = true
      } catch (error) {
        this.$message.error('获取统计信息失败')
        console.error('获取统计信息失败:', error)
      }
    },

    async setActive(id) {
      try {
        await personnelService.setPersonnelActive(id)
        this.$message.success('已设置为在职状态')
        await this.fetchPersonnel()
      } catch (error) {
        this.$message.error('操作失败')
        console.error('设置在职状态失败:', error)
      }
    },

    async setInactive(id) {
      try {
        await this.$confirm('确认设置该人员为已卸任状态？', '确认操作', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        await personnelService.setPersonnelInactive(id)
        this.$message.success('已设置为已卸任状态')
        await this.fetchPersonnel()
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('操作失败')
          console.error('设置已卸任状态失败:', error)
        }
      }
    },

    async deletePersonnel(id) {
      try {
        await this.$confirm('确认删除该人员信息？此操作不可恢复。', '确认删除', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        await personnelService.deletePersonnel(id)
        this.$message.success('删除成功')
        await this.fetchPersonnel()
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('删除失败')
          console.error('删除人员失败:', error)
        }
      }
    },

    async handleFormSubmit() {
      this.dialogVisible = false
      await this.fetchPersonnel()
    }
  }
}
</script>

<style scoped>
.personnel-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
