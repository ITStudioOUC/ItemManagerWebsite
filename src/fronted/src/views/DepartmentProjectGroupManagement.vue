<template>
  <div>
    <AppHeader />
    <div class="management-container">
      <el-row :gutter="20">
        <!-- 部门管理 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>部门管理</span>
                <el-button type="primary" @click="showAddDepartmentDialog">
                  <el-icon><Plus /></el-icon>
                  添加部门
                </el-button>
              </div>
            </template>

            <el-table :data="departments" style="width: 100%" v-loading="departmentLoading">
              <el-table-column prop="name" label="部门名称" />
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button size="small" @click="editDepartment(scope.row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteDepartment(scope.row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>

        <!-- 项目组管理 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>项目组管理</span>
                <el-button type="primary" @click="showAddProjectGroupDialog">
                  <el-icon><Plus /></el-icon>
                  添加项目组
                </el-button>
              </div>
            </template>

            <div class="filter-section" style="margin-bottom: 15px;">
              <el-select v-model="departmentFilter" placeholder="筛选部门" clearable @change="filterProjectGroups">
                <el-option label="全部部门" value="" />
                <el-option
                  v-for="dept in departments"
                  :key="dept.id"
                  :label="dept.name"
                  :value="dept.id" />
              </el-select>
            </div>

            <el-table :data="filteredProjectGroups" style="width: 100%" v-loading="projectGroupLoading">
              <el-table-column prop="name" label="项目组名称" />
              <el-table-column label="所属部门" min-width="150">
                <template #default="scope">
                  <el-tag v-for="dept in scope.row.departments_info" :key="dept.id" size="small" style="margin-right: 5px;">
                    {{ dept.name }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="描述" show-overflow-tooltip />
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button size="small" @click="editProjectGroup(scope.row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteProjectGroup(scope.row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>

      <!-- 添加/编辑部门对话框 -->
      <el-dialog :title="departmentDialogTitle" v-model="departmentDialogVisible" width="40%">
        <el-form :model="departmentForm" :rules="departmentRules" ref="departmentFormRef" label-width="100px">
          <el-form-item label="部门名称" prop="name">
            <el-input v-model="departmentForm.name" placeholder="请输入部门名称" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="departmentDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitDepartmentForm">保存</el-button>
        </template>
      </el-dialog>

      <!-- 添加/编辑项目组对话框 -->
      <el-dialog :title="projectGroupDialogTitle" v-model="projectGroupDialogVisible" width="50%">
        <el-form :model="projectGroupForm" :rules="projectGroupRules" ref="projectGroupFormRef" label-width="100px">
          <el-form-item label="项目组名称" prop="name">
            <el-input v-model="projectGroupForm.name" placeholder="请输入项目组名称" />
          </el-form-item>
          <el-form-item label="所属部门" prop="departments">
            <el-select v-model="projectGroupForm.departments" placeholder="请选择所属部门" multiple>
              <el-option
                v-for="dept in departments"
                :key="dept.id"
                :label="dept.name"
                :value="dept.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="项目组描述" prop="description">
            <el-input
              v-model="projectGroupForm.description"
              type="textarea"
              :rows="3"
              placeholder="请输入项目组描述（可选）" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="projectGroupDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitProjectGroupForm">保存</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import {financeService, projectGroupService} from '@/services/api'
import AppHeader from '@/components/AppHeader.vue'
import {Plus} from '@element-plus/icons-vue'

export default {
  name: 'DepartmentProjectGroupManagement',
  components: {
    AppHeader,
    Plus
  },
  data() {
    return {
      departments: [],
      projectGroups: [],
      departmentLoading: false,
      projectGroupLoading: false,

      // 筛选
      departmentFilter: '',

      // 部门对话框
      departmentDialogVisible: false,
      departmentDialogTitle: '',
      departmentForm: {
        id: null,
        name: ''
      },
      departmentRules: {
        name: [
          { required: true, message: '请输入部门名称', trigger: 'blur' }
        ]
      },

      // 项目组对话框
      projectGroupDialogVisible: false,
      projectGroupDialogTitle: '',
      projectGroupForm: {
        id: null,
        name: '',
        departments: [],
        description: ''
      },
      projectGroupRules: {
        name: [
          { required: true, message: '请输入项目组名称', trigger: 'blur' }
        ],
        departments: [
          { required: true, message: '请选择所属部门', trigger: 'change' }
        ]
      }
    }
  },
  computed: {
    filteredProjectGroups() {
      if (!this.departmentFilter) {
        return this.projectGroups
      }
      return this.projectGroups.filter(group =>
        group.departments && group.departments.includes(parseInt(this.departmentFilter))
      )
    }
  },
  async created() {
    await this.loadData()
  },
  methods: {
    async loadData() {
      await Promise.all([
        this.fetchDepartments(),
        this.fetchProjectGroups()
      ])
    },

    async fetchDepartments() {
      this.departmentLoading = true
      try {
        const response = await financeService.getAllDepartments()
        this.departments = response.data
      } catch (error) {
        this.$message.error('获取部门列表失败')
        console.error('获取部门列表失败:', error)
      } finally {
        this.departmentLoading = false
      }
    },

    async fetchProjectGroups() {
      this.projectGroupLoading = true
      try {
        const response = await projectGroupService.getAllProjectGroups()
        this.projectGroups = response.data
      } catch (error) {
        this.$message.error('获取项目组列表失败')
        console.error('获取项目组列表失败:', error)
      } finally {
        this.projectGroupLoading = false
      }
    },

    filterProjectGroups() {
      // 筛选逻辑在computed中处理
    },

    // 部门管理方法
    showAddDepartmentDialog() {
      this.departmentForm = { id: null, name: '' }
      this.departmentDialogTitle = '添加部门'
      this.departmentDialogVisible = true
    },

    editDepartment(department) {
      this.departmentForm = { ...department }
      this.departmentDialogTitle = '编辑部门'
      this.departmentDialogVisible = true
    },

    async submitDepartmentForm() {
      try {
        await this.$refs.departmentFormRef.validate()

        if (this.departmentForm.id) {
          // 更新部门
          await financeService.updateDepartment(this.departmentForm.id, this.departmentForm)
          this.$message.success('部门更新成功')
        } else {
          // 创建部门
          await financeService.createDepartment(this.departmentForm)
          this.$message.success('部门创建成功')
        }

        this.departmentDialogVisible = false
        await this.fetchDepartments()
      } catch (error) {
        this.$message.error('操作失败')
        console.error('部门操作失败:', error)
      }
    },

    async deleteDepartment(id) {
      try {
        await this.$confirm('确认删除该部门？删除后所有相关数据将受到影响。', '确认删除', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        await financeService.deleteDepartment(id)
        this.$message.success('部门删除成功')
        await this.fetchDepartments()
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('删除失败')
          console.error('删除部门失败:', error)
        }
      }
    },

    // 项目组管理方法
    showAddProjectGroupDialog() {
      this.projectGroupForm = { id: null, name: '', departments: [], description: '' }
      this.projectGroupDialogTitle = '添加项目组'
      this.projectGroupDialogVisible = true
    },

    editProjectGroup(projectGroup) {
      this.projectGroupForm = {
        ...projectGroup,
        departments: projectGroup.departments || []
      }
      this.projectGroupDialogTitle = '编辑项目组'
      this.projectGroupDialogVisible = true
    },

    async submitProjectGroupForm() {
      try {
        await this.$refs.projectGroupFormRef.validate()

        if (this.projectGroupForm.id) {
          // 更新项目组
          await projectGroupService.updateProjectGroup(this.projectGroupForm.id, this.projectGroupForm)
          this.$message.success('项目组更新成功')
        } else {
          // 创建项目组
          await projectGroupService.createProjectGroup(this.projectGroupForm)
          this.$message.success('项目组创建成功')
        }

        this.projectGroupDialogVisible = false
        await this.fetchProjectGroups()
      } catch (error) {
        this.$message.error('操作失败')
        console.error('项目组操作失败:', error)
      }
    },

    async deleteProjectGroup(id) {
      try {
        await this.$confirm('确认删除该项目组？', '确认删除', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        await projectGroupService.deleteProjectGroup(id)
        this.$message.success('项目组删除成功')
        await this.fetchProjectGroups()
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('删除失败')
          console.error('删除项目组失败:', error)
        }
      }
    }
  }
}
</script>

<style scoped>
.management-container {
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
  padding: 10px 0;
}
</style>
