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
              <el-button type="success" :loading="downloadingTemplate" @click="handleDownloadTemplate">
                <el-icon><Download/></el-icon>
                下载样表
              </el-button>
              <el-button type="warning" :loading="exporting" @click="handleExport">
                <el-icon><Download/></el-icon>
                导出人员
              </el-button>
              <el-button type="info" :loading="importing" @click="triggerImport">
                <el-icon><UploadFilled/></el-icon>
                导入人员
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
            <el-form-item label="年级">
              <el-input
                v-model="filters.grade"
                placeholder="输入年级"
                style="min-width: 200px"
                clearable
                @change="fetchRecords">
              </el-input>
            </el-form-item>
            <el-form-item label="姓名">
              <el-input
                v-model="filters.personnel"
                placeholder="输入人员姓名"
                style="min-width: 200px"
                clearable
                @change="fetchRecords">
              </el-input>
            </el-form-item>
            <el-form-item label="分数筛选">
              <el-row :gutter="10" style="min-width: 300px">
                <el-col :span="8">
                  <el-select
                    v-model="filters.scoreCondition"
                    placeholder="条件"
                    @change="applyScoreFilter">
                    <el-option label="高于" value="gt"/>
                    <el-option label="等于" value="eq"/>
                    <el-option label="低于" value="lt"/>
                  </el-select>
                </el-col>
                <el-col :span="16">
                  <el-input-number
                    v-model="filters.scoreValue"
                    placeholder="输入分数"
                    :step="0.01"
                    :precision="2"
                    style="width: 100%"
                    @change="applyScoreFilter"/>
                </el-col>
              </el-row>
            </el-form-item>
          </el-form>
        </div>

        <el-table
          :data="filteredPersonnelList"
          style="width: 100%"
          v-loading="loading"
          stripe
          table-layout="auto">
          <el-table-column prop="department_name" label="所属部门" min-width="150"/>
          <el-table-column prop="grade" label="年级" min-width="120"/>
          <el-table-column prop="personnel" label="姓名" min-width="120"/>
          <el-table-column label="目前总分" min-width="120">
            <template #default="scope">
              <el-tag :type="scope.row.total_score >= 0 ? 'success' : 'danger'">
                {{ formatNumber(scope.row.total_score) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="scope">
              <el-button size="small" type="primary" @click="editPersonnel(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="confirmDelete(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="summary-bar">
          <div>
            <span>人员数：{{ filteredPersonnelList.length }}</span>
            <span>平均分：{{ filteredAverageScore }}</span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { evaluationService, financeService } from '@/services/api'
import AppHeader from '@/components/AppHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Download, UploadFilled } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'

export default {
  name: 'EvaluationRecordList',
  components: {
    AppHeader,
    Refresh,
    Download,
    UploadFilled
  },
  data() {
    return {
      loading: false,
      exporting: false,
      importing: false,
      downloadingTemplate: false,
      personnelList: [],
      departments: [],
      filters: {
        department: '',
        personnel: '',
        grade: '',
        scoreCondition: '',
        scoreValue: null
      }
    }
  },
  computed: {
    filteredPersonnelList() {
      let filtered = [...this.personnelList]

      if (this.filters.scoreCondition && this.filters.scoreValue !== null && this.filters.scoreValue !== '') {
        const value = Number(this.filters.scoreValue)
        filtered = filtered.filter(person => {
          const score = Number(person.total_score || 0)
          switch (this.filters.scoreCondition) {
            case 'gt':
              return score > value
            case 'eq':
              return Math.abs(score - value) < 0.01
            case 'lt':
              return score < value
            default:
              return true
          }
        })
      }

      return filtered
    },
    averageScore() {
      if (!this.personnelList || this.personnelList.length === 0) {
        return '0.00'
      }
      const total = this.personnelList.reduce((sum, item) => sum + Number(item.total_score || 0), 0)
      const average = total / this.personnelList.length
      return average.toFixed(2)
    },
    filteredAverageScore() {
      if (!this.filteredPersonnelList || this.filteredPersonnelList.length === 0) {
        return '0.00'
      }
      const total = this.filteredPersonnelList.reduce((sum, item) => sum + Number(item.total_score || 0), 0)
      const average = total / this.filteredPersonnelList.length
      return average.toFixed(2)
    }
  },
  async mounted() {
    await this.fetchDepartments()
    await this.fetchRecords()
  },
  methods: {
    async fetchDepartments() {
      try {
        const resp = await financeService.getAllDepartments()
        this.departments = resp.data
      } catch (error) {
        console.error('获取部门失败:', error)
        ElMessage.error('获取部门信息失败')
      }
    },
    buildQueryParams() {
      const params = {}
      const department = this.parseIdForApi(this.filters.department)
      if (department !== null) params.department = department
      if (this.filters.personnel && this.filters.personnel.trim()) {
        params.personnel = this.filters.personnel.trim()
      }
      if (this.filters.grade && this.filters.grade.trim()) {
        params.grade = this.filters.grade.trim()
      }
      return params
    },
    async fetchRecords() {
      this.loading = true
      try {
        const resp = await evaluationService.getPersonnelSummary(this.buildQueryParams())
        this.personnelList = resp.data
      } catch (error) {
        console.error('获取人员列表失败:', error)
        ElMessage.error('加载人员列表失败')
      } finally {
        this.loading = false
      }
    },
    resetFilters() {
      this.filters = {
        department: '',
        personnel: '',
        grade: '',
        scoreCondition: '',
        scoreValue: null
      }
      this.fetchRecords()
    },
    applyScoreFilter() {
    },
    editPersonnel(row) {
      this.$router.push({
        name: 'EvaluationRecordDetail',
        params: {
          personnel: row.personnel
        },
        query: {
          department: row.department_name,
          grade: row.grade || ''
        }
      })
    },
    async confirmDelete(row) {
      try {
        await ElMessageBox.confirm(
          `确定要删除 ${row.personnel} 的所有考评记录吗？此操作不可恢复！`,
          '删除确认',
          {
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        // 调用API删除该人员的所有记录
        await evaluationService.deletePersonnelRecords(
          row.personnel,
          row.department_name,
          row.grade || ''
        )

        ElMessage.success('删除成功')
        // 刷新列表
        await this.fetchRecords()
      } catch (error) {
        if (error !== 'cancel' && error !== 'close') {
          console.error('删除失败:', error)
          const errorMsg = error.response?.data?.detail || '删除失败'
          ElMessage.error(errorMsg)
        }
      }
    },
    async handleDownloadTemplate() {
      this.downloadingTemplate = true
      try {
        const response = await evaluationService.downloadTemplate()
        const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = '人员导入样表.xlsx'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        ElMessage.success('下载成功')
      } catch (error) {
        console.error('下载样表失败:', error)
        ElMessage.error('下载样表失败')
      } finally {
        this.downloadingTemplate = false
      }
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
        await evaluationService.importPersonnelRecords(file)
        ElMessage.success('导入成功')
        await this.fetchRecords()
      } catch (error) {
        console.error('导入失败:', error)
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
    async handleExport() {
      if (!this.filteredPersonnelList.length) {
        ElMessage.warning('暂无数据可导出')
        return
      }
      this.exporting = true
      try {
        const params = this.buildQueryParams()
        const response = await evaluationService.exportPersonnelRecords(params)
        const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
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
        console.error('导出失败:', error)
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
      return `人员考评记录_${dateStr}.xlsx`
    },
    formatNumber(value) {
      const num = Number(value || 0)
      return num.toFixed(2)
    },
    parseIdForApi(value) {
      if (value === '' || value === null || value === undefined) return null
      const numeric = Number(value)
      return Number.isNaN(numeric) ? value : numeric
    }
  }
}
</script>

<style scoped>
.evaluation-container {
  margin: 20px auto;
  padding: 0 20px;
  width: 100%;
  box-sizing: border-box;
}

.evaluation-container :deep(.el-card) {
  width: 100%;
}

.evaluation-container :deep(.el-card__body) {
  width: 100%;
  box-sizing: border-box;
}

.evaluation-container :deep(.el-table) {
  width: 100% !important;
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
  width: 100%;
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
  width: 100%;
  box-sizing: border-box;
}

.summary-bar span {
  margin-right: 20px;
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
