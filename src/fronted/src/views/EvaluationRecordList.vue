<template>
  <div>
    <AppHeader/>
    <div class="evaluation-container">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>考评记录</span>
            <div class="header-actions">
              <el-button @click="resetFilters">
                <el-icon><Refresh/></el-icon>
                重置筛选
              </el-button>
              <el-button type="primary" @click="openCreateDialog">
                <el-icon><Plus/></el-icon>
                新增记录
              </el-button>
              <el-button type="success" @click="openSummaryDialog">
                <el-icon><Search/></el-icon>
                查看总表
              </el-button>
              <el-button type="warning" :loading="exporting" @click="handleExport">
                <el-icon><Download/></el-icon>
                导出总表
              </el-button>
              <el-button type="info" :loading="importing" @click="triggerImport">
                <el-icon><UploadFilled/></el-icon>
                导入总表
              </el-button>
              <input
                ref="importInput"
                type="file"
                style="display: none"
                accept=".xlsx,.xls,.csv"
                @change="handleImportChange">
            </div>
          </div>
        </template>

        <div class="filter-section">
          <el-form :inline="true" label-width="80px" class="filter-form">
            <el-form-item label="部门">
              <el-select
                v-model="filters.department"
                placeholder="选择部门"
                style="min-width: 200px"
                clearable
                @change="fetchRecords">
                <el-option
                  v-for="dept in departments"
                  :key="dept.id"
                  :label="dept.name"
                  :value="String(dept.id)"/>
              </el-select>
            </el-form-item>
            <el-form-item label="人员">
              <el-select
                v-model="filters.personnel"
                placeholder="选择人员"
                style="min-width: 200px"
                clearable
                filterable
                @change="fetchRecords">
                <el-option
                  v-for="person in personnel"
                  :key="person.id"
                  :label="person.name"
                  :value="String(person.id)"/>
              </el-select>
            </el-form-item>
            <el-form-item label="日期">
              <el-date-picker
                v-model="filters.dateRange"
                type="daterange"
                unlink-panels
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
                @change="fetchRecords"/>
            </el-form-item>
            <el-form-item label="搜索">
              <el-input
                v-model="filters.keyword"
                placeholder="事项说明 / 备注 / 人员"
                clearable
                @change="fetchRecords">
                <template #prefix>
                  <el-icon><Search/></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-form>
        </div>

        <el-table
          :data="records"
          style="width: 100%"
          v-loading="loading"
          stripe>
          <el-table-column prop="evaluation_date" label="考评日期" width="120"/>
          <el-table-column prop="department_name" label="部门" width="150"/>
          <el-table-column prop="personnel_name" label="姓名" width="120"/>
          <el-table-column prop="item_description" label="加/扣分事项说明" min-width="220" show-overflow-tooltip/>
          <el-table-column prop="bonus_score" label="加分" width="90">
            <template #default="scope">
              <span class="bonus-text">+{{ formatNumber(scope.row.bonus_score) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="deduction_score" label="扣分" width="90">
            <template #default="scope">
              <span class="deduction-text">-{{ formatNumber(scope.row.deduction_score) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="total_score" label="总计分数" width="110">
            <template #default="scope">
              <el-tag :type="scope.row.total_score >= 0 ? 'success' : 'danger'">
                {{ formatNumber(scope.row.total_score) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="remarks" label="备注" min-width="160" show-overflow-tooltip/>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="confirmDelete(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="summary-bar">
          <div>
            <span>记录数：{{ records.length }}</span>
            <span>总加分：{{ formatNumber(totalBonus) }}</span>
            <span>总扣分：{{ formatNumber(totalDeduction) }}</span>
            <span>综合分：{{ formatNumber(totalScore) }}</span>
          </div>
        </div>
      </el-card>

      <el-dialog
        title="个人分数总表"
        v-model="summaryDialogVisible"
        width="640px"
        destroy-on-close>
        <div v-if="personSummary.length">
          <el-table
            :data="personSummary"
            border
            size="small"
            style="width: 100%">
            <el-table-column prop="name" label="姓名" min-width="140"/>
            <el-table-column label="总加分" width="120">
              <template #default="scope">
                <span class="bonus-text">+{{ formatNumber(scope.row.bonus) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="总扣分" width="120">
              <template #default="scope">
                <span class="deduction-text">-{{ formatNumber(scope.row.deduction) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="综合分" width="120">
              <template #default="scope">
                <el-tag :type="scope.row.total >= 0 ? 'success' : 'danger'">
                  {{ formatNumber(scope.row.total) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-else class="summary-empty">
          暂无数据
        </div>
        <template #footer>
          <div class="summary-footer">
            <div>
              <span>总加分：{{ formatNumber(summaryTotals.bonus) }}</span>
              <span>总扣分：{{ formatNumber(summaryTotals.deduction) }}</span>
              <span>综合分：{{ formatNumber(summaryTotals.total) }}</span>
            </div>
            <el-button @click="summaryDialogVisible = false">关闭</el-button>
          </div>
        </template>
      </el-dialog>

      <el-dialog
        :title="isEditing ? '编辑考评记录' : '新增考评记录'"
        v-model="dialogVisible"
        width="520px"
        destroy-on-close>
        <el-form
          ref="recordFormRef"
          :model="form"
          :rules="formRules"
          label-width="110px">
          <el-form-item label="所属部门" prop="department">
            <el-select v-model="form.department" placeholder="请选择部门" style="width: 260px">
              <el-option
                v-for="dept in departments"
                :key="dept.id"
                :label="dept.name"
                :value="String(dept.id)"/>
            </el-select>
          </el-form-item>
          <el-form-item label="人员" prop="personnel">
            <el-select v-model="form.personnel" placeholder="请选择人员" filterable style="width: 260px">
              <el-option
                v-for="person in personnel"
                :key="person.id"
                :label="person.name"
                :value="String(person.id)"/>
            </el-select>
          </el-form-item>
          <el-form-item label="考评日期" prop="evaluation_date">
            <el-date-picker
              v-model="form.evaluation_date"
              type="date"
              placeholder="请选择日期"
              value-format="YYYY-MM-DD"/>
          </el-form-item>
          <el-form-item label="事项说明" prop="item_description">
            <el-input
              v-model="form.item_description"
              placeholder="请输入加/扣分的事项说明"
              maxlength="255"
              show-word-limit/>
          </el-form-item>
          <el-form-item label="加分数值" prop="bonus_score">
            <el-input-number
              v-model="form.bonus_score"
              :min="0"
              :precision="2"
              :step="0.5"
              controls-position="right"
            />
          </el-form-item>
          <el-form-item label="扣分数值" prop="deduction_score">
            <el-input-number
              v-model="form.deduction_score"
              :min="0"
              :precision="2"
              :step="0.5"
              controls-position="right"
            />
          </el-form-item>
          <el-form-item label="备注">
            <el-input
              v-model="form.remarks"
              placeholder="可填写附加说明"
              type="textarea"
              :rows="3"
              maxlength="255"
              show-word-limit/>
          </el-form-item>
        </el-form>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" :loading="saving" @click="handleSubmit">
              {{ isEditing ? '保存修改' : '创建记录' }}
            </el-button>
          </div>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import { evaluationService, financeService, personnelService } from '@/services/api'
import AppHeader from '@/components/AppHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search, Download, UploadFilled } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'

export default {
  name: 'EvaluationRecordList',
  components: {
    AppHeader,
    Plus,
    Refresh,
    Search,
    Download,
    UploadFilled
  },
  data() {
    return {
      loading: false,
      saving: false,
      exporting: false,
      importing: false,
      records: [],
      departments: [],
      personnel: [],
      dialogVisible: false,
      summaryDialogVisible: false,
      isEditing: false,
      currentRecordId: null,
      filters: {
        department: '',
        personnel: '',
        keyword: '',
        dateRange: []
      },
      form: this.getEmptyForm(),
      formRules: {
        department: [{ required: true, message: '请选择部门', trigger: 'change' }],
        personnel: [{ required: true, message: '请选择人员', trigger: 'change' }],
        evaluation_date: [{ required: true, message: '请选择考评日期', trigger: 'change' }],
        item_description: [
          { required: true, message: '请填写事项说明', trigger: 'blur' },
          { min: 1, max: 255, message: '长度在 1 到 255 个字符', trigger: 'blur' }
        ],
        bonus_score: [{ type: 'number', min: 0, message: '加分数值不能为负', trigger: 'change' }],
        deduction_score: [{ type: 'number', min: 0, message: '扣分数值不能为负', trigger: 'change' }]
      }
    }
  },
  computed: {
    totalBonus() {
      return this.records.reduce((sum, item) => sum + Number(item.bonus_score || 0), 0)
    },
    personSummary() {
      const summaryMap = new Map()
      this.records.forEach(record => {
        const id = this.extractPersonKey(record)
        const existing = summaryMap.get(id) || {
          id,
          name: this.resolvePersonName(record),
          bonus: 0,
          deduction: 0,
          total: 0
        }
        existing.bonus += Number(record.bonus_score || 0)
        existing.deduction += Number(record.deduction_score || 0)
        existing.total += Number(record.total_score || 0)
        summaryMap.set(id, existing)
      })
      return Array.from(summaryMap.values()).sort((a, b) => a.name.localeCompare(b.name, 'zh-Hans-CN'))
    },
    summaryTotals() {
      return this.personSummary.reduce(
        (acc, item) => {
          acc.bonus += item.bonus
          acc.deduction += item.deduction
          acc.total += item.total
          return acc
        },
        { bonus: 0, deduction: 0, total: 0 }
      )
    },
    totalDeduction() {
      return this.records.reduce((sum, item) => sum + Number(item.deduction_score || 0), 0)
    },
    totalScore() {
      return this.records.reduce((sum, item) => sum + Number(item.total_score || 0), 0)
    }
  },
  async mounted() {
    await Promise.all([this.fetchDepartments(), this.fetchPersonnel()])
    await this.fetchRecords()
  },
  methods: {
    getEmptyForm() {
      const today = new Date().toISOString().slice(0, 10)
      return {
        department: '',
        personnel: '',
        evaluation_date: today,
        item_description: '',
        bonus_score: 0,
        deduction_score: 0,
        remarks: ''
      }
    },
    async fetchDepartments() {
      try {
        const resp = await financeService.getAllDepartments()
        this.departments = resp.data
      } catch (error) {
        console.error('获取部门失败:', error)
        ElMessage.error('获取部门信息失败')
      }
    },
    async fetchPersonnel() {
      try {
        const resp = await personnelService.getAllPersonnel()
        this.personnel = resp.data
      } catch (error) {
        console.error('获取人员失败:', error)
        ElMessage.error('获取人员信息失败')
      }
    },
    buildQueryParams() {
      const params = {}
      const department = this.parseIdForApi(this.filters.department)
      const personnel = this.parseIdForApi(this.filters.personnel)
      if (department !== null) params.department = department
      if (personnel !== null) params.personnel = personnel
      if (this.filters.keyword) params.search = this.filters.keyword
      if (this.filters.dateRange && this.filters.dateRange.length === 2) {
        params.date_from = this.filters.dateRange[0]
        params.date_to = this.filters.dateRange[1]
      }
      return params
    },
    async fetchRecords() {
      this.loading = true
      try {
        const resp = await evaluationService.getEvaluationRecords(this.buildQueryParams())
        this.records = resp.data
      } catch (error) {
        console.error('获取考评记录失败:', error)
        ElMessage.error('加载考评记录失败')
      } finally {
        this.loading = false
      }
    },
    resetFilters() {
      this.filters = {
        department: '',
        personnel: '',
        keyword: '',
        dateRange: []
      }
      this.fetchRecords()
    },
    openCreateDialog() {
      this.isEditing = false
      this.currentRecordId = null
      this.form = this.getEmptyForm()
      this.dialogVisible = true
    },
    openSummaryDialog() {
      this.summaryDialogVisible = true
    },
    triggerImport() {
      this.$refs.importInput?.click()
    },
    async handleImportChange(event) {
      const files = event.target.files
      if (!files || !files.length) return
      const file = files[0]
      this.importing = true
      try {
        await evaluationService.importEvaluationRecords(file)
        ElMessage.success('导入成功')
        await this.fetchRecords()
      } catch (error) {
        console.error('导入考评记录失败:', error)
        const detail = error.response?.data?.detail
        const errorList = error.response?.data?.errors
        let message = detail || '导入失败'
        if (Array.isArray(errorList) && errorList.length) {
          message = `${message}: ${errorList[0]}`
        }
        ElMessage.error(message)
      } finally {
        this.importing = false
        if (event.target) event.target.value = ''
      }
    },
    openEditDialog(record) {
      this.isEditing = true
      this.currentRecordId = record.id
      this.form = {
        department: this.toStringId(this.findDepartmentId(record)),
        personnel: this.toStringId(this.findPersonnelId(record)),
        evaluation_date: record.evaluation_date,
        item_description: record.item_description,
        bonus_score: Number(record.bonus_score),
        deduction_score: Number(record.deduction_score),
        remarks: record.remarks || ''
      }
      this.dialogVisible = true
    },
    handleSubmit() {
      this.$refs.recordFormRef.validate(async valid => {
        if (!valid) return

        this.saving = true
        const payload = {
          ...this.form,
          department: this.parseIdForApi(this.form.department),
          personnel: this.parseIdForApi(this.form.personnel),
          bonus_score: Number(this.form.bonus_score) || 0,
          deduction_score: Number(this.form.deduction_score) || 0
        }

        try {
          if (this.isEditing && this.currentRecordId) {
            await evaluationService.updateEvaluationRecord(this.currentRecordId, payload)
            ElMessage.success('更新考评记录成功')
          } else {
            await evaluationService.createEvaluationRecord(payload)
            ElMessage.success('新增考评记录成功')
          }
          this.dialogVisible = false
          await this.fetchRecords()
        } catch (error) {
          console.error('保存考评记录失败:', error)
          ElMessage.error('保存考评记录失败')
        } finally {
          this.saving = false
        }
      })
    },
    async confirmDelete(record) {
      try {
        await ElMessageBox.confirm(
          `确定要删除 ${record.personnel_name} 在 ${record.evaluation_date} 的考评记录吗？`,
          '删除确认',
          {
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        await evaluationService.deleteEvaluationRecord(record.id)
        ElMessage.success('删除成功')
        await this.fetchRecords()
      } catch (error) {
        if (error !== 'cancel' && error !== 'close') {
          console.error('删除考评记录失败:', error)
          ElMessage.error('删除考评记录失败')
        }
      }
    },
    formatNumber(value) {
      const num = Number(value || 0)
      return num.toFixed(2)
    },
    toStringId(value) {
      if (value === null || value === undefined || value === '') return ''
      if (typeof value === 'object') {
        return value.id !== undefined && value.id !== null ? String(value.id) : ''
      }
      return String(value)
    },
    parseIdForApi(value) {
      if (value === '' || value === null || value === undefined) return null
      const numeric = Number(value)
      return Number.isNaN(numeric) ? value : numeric
    },
    findDepartmentId(record) {
      if (record?.department_id !== undefined && record.department_id !== null) {
        return record.department_id
      }
      if (record?.department) {
        if (typeof record.department === 'object') {
          const deptObj = record.department
          if (deptObj.id !== undefined && deptObj.id !== null) return deptObj.id
        } else {
          const matchById = this.departments.find(dept => String(dept.id) === String(record.department))
          if (matchById) return matchById.id
          const matchByName = this.departments.find(dept => dept.name === record.department || dept.name === record.department_name)
          if (matchByName) return matchByName.id
        }
      }
      if (record?.department_name) {
        const matchByName = this.departments.find(dept => dept.name === record.department_name)
        if (matchByName) return matchByName.id
      }
      return ''
    },
    findPersonnelId(record) {
      if (record?.personnel_id !== undefined && record.personnel_id !== null) {
        return record.personnel_id
      }
      if (record?.personnel) {
        if (typeof record.personnel === 'object') {
          const personObj = record.personnel
          if (personObj.id !== undefined && personObj.id !== null) return personObj.id
        } else {
          const matchById = this.personnel.find(person => String(person.id) === String(record.personnel))
          if (matchById) return matchById.id
          const matchByName = this.personnel.find(person => person.name === record.personnel || person.name === record.personnel_name)
          if (matchByName) return matchByName.id
        }
      }
      if (record?.personnel_name) {
        const matchByName = this.personnel.find(person => person.name === record.personnel_name)
        if (matchByName) return matchByName.id
      }
      return ''
    },
    extractPersonKey(record) {
      if (record?.personnel_id !== undefined && record.personnel_id !== null) {
        return `id:${record.personnel_id}`
      }
      if (record?.personnel && typeof record.personnel === 'object' && record.personnel.id !== undefined && record.personnel.id !== null) {
        return `id:${record.personnel.id}`
      }
      if (record?.personnel) {
        return `person:${record.personnel}`
      }
      if (record?.personnel_name) {
        return `name:${record.personnel_name}`
      }
      return `row:${record.id ?? Math.random()}`
    },
    resolvePersonName(record) {
      if (record?.personnel_name) return record.personnel_name
      if (record?.personnel && typeof record.personnel === 'object' && record.personnel.name) return record.personnel.name
      if (record?.personnel) return record.personnel
      return '未命名人员'
    },
    async handleExport() {
      if (!this.personSummary.length) {
        ElMessage.warning('暂无数据可导出')
        return
      }
      this.exporting = true
      try {
        const params = this.buildQueryParams()
        const response = await evaluationService.exportEvaluationRecords(params)
        const workbook = XLSX.read(response.data, { type: 'array' })
        const wbout = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
        const blob = new Blob([wbout], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        const filename = this.extractFilename(response.headers?.['content-disposition']) || this.generateExportFilename()
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        ElMessage.success('导出成功')
      } catch (error) {
        console.error('导出考评记录失败:', error)
        ElMessage.error('导出失败')
      } finally {
        this.exporting = false
      }
    },
    extractFilename(disposition) {
      if (!disposition) return ''
      const match = /filename="?([^"]+)"?/i.exec(disposition)
      return match ? decodeURIComponent(match[1]) : ''
    },
    generateExportFilename() {
      const now = new Date()
      const pad = value => value.toString().padStart(2, '0')
      const dateStr = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`
      return `考评总表_${dateStr}.xlsx`
    }
  }
}
</script>

<style scoped>
.evaluation-container {
  max-width: 1200px;
  margin: 20px auto;
  padding: 0 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.summary-bar {
  margin-top: 16px;
  padding: 14px 20px;
  background: #f5f7fa;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #606266;
}

.summary-bar span {
  margin-right: 20px;
}

.summary-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-footer span {
  margin-right: 16px;
  color: #606266;
}

.summary-empty {
  padding: 40px 0;
  text-align: center;
  color: #909399;
}

.dialog-footer {
  text-align: right;
}

.bonus-text {
  color: #67c23a;
  font-weight: 600;
}

.deduction-text {
  color: #f56c6c;
  font-weight: 600;
}

@media (max-width: 768px) {
  .evaluation-container {
    padding: 0 10px;
  }

  .filter-form {
    flex-direction: column;
  }
}
</style>

