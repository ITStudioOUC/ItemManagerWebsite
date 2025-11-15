<template>
  <div>
    <AppHeader/>
    <div class="detail-container">
      <el-card>
        <template #header>
          <div class="card-header">
            <el-button @click="$router.go(-1)">
              <el-icon><ArrowLeft/></el-icon>
              返回
            </el-button>
            <span>考评记录详情</span>
            <div></div>
          </div>
        </template>

        <!-- 基本信息 -->
        <div class="info-section">
          <h3>基本信息</h3>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="部门">{{ personnelInfo.department_name }}</el-descriptions-item>
            <el-descriptions-item label="年级">{{ personnelInfo.grade || '-' }}</el-descriptions-item>
            <el-descriptions-item label="姓名">{{ personnelInfo.personnel }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 统计信息 -->
        <div class="statistics-section">
          <h3>统计信息</h3>
          <el-row :gutter="24">
            <el-col :span="8">
              <el-statistic title="总分" :value="personnelInfo.total_score">
                <template #suffix>
                  <span class="bonus-text">分</span>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="4">
              <el-statistic title="总加分数" :value="personnelInfo.total_bonus - 39">
                <template #suffix>
                  <span class="bonus-text">分</span>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="4">
              <el-statistic title="总扣分数" :value="personnelInfo.total_deduction">
                <template #suffix>
                  <span class="deduction-text">分</span>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="4">
              <el-statistic title="加分次数" :value="personnelInfo.bonus_count">
                <template #suffix>
                  <span>次</span>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="4">
              <el-statistic title="扣分次数" :value="personnelInfo.deduction_count">
                <template #suffix>
                  <span>次</span>
                </template>
              </el-statistic>
            </el-col>
          </el-row>
        </div>

        <!-- 记录列表 -->
        <div class="records-section">
          <div class="section-header">
            <h3>考评记录</h3>
            <el-button type="primary" @click="openCreateDialog">
              <el-icon><Plus/></el-icon>
              新增记录
            </el-button>
          </div>
          <el-table
            :data="records"
            style="width: 100%"
            v-loading="loading"
            stripe>
            <el-table-column prop="item_description" label="扣分/加分说明" min-width="200" show-overflow-tooltip/>
            <el-table-column prop="evaluation_date" label="考评时间" width="120"/>
            <el-table-column label="分值" width="120">
              <template #default="scope">
                <span :class="getScoreClass(scope.row)">
                  {{ formatScore(scope.row) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="remarks" label="备注" min-width="200" show-overflow-tooltip/>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="confirmDelete(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>

      <!-- 新增/编辑对话框 -->
      <el-dialog
        :title="isEditing ? '编辑记录' : '新增记录'"
        v-model="dialogVisible"
        width="600px"
        destroy-on-close>
        <el-form
          ref="recordFormRef"
          :model="form"
          :rules="formRules"
          label-width="120px">
          <el-form-item label="扣分/加分说明" prop="item_description">
            <el-input
              v-model="form.item_description"
              placeholder="请输入扣分/加分说明"
              maxlength="255"
              show-word-limit/>
          </el-form-item>
          <el-form-item label="考评时间" prop="evaluation_date">
            <el-date-picker
              v-model="form.evaluation_date"
              type="date"
              placeholder="请选择日期"
              value-format="YYYY-MM-DD"
              style="width: 100%"/>
          </el-form-item>
          <el-form-item label="分值" prop="score">
            <el-input-number
              v-model="form.score"
              :precision="2"
              :step="0.5"
              controls-position="right"
              placeholder="正数为加分，负数为扣分"
              style="width: 100%"/>
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
import { evaluationService, financeService } from '@/services/api'
import AppHeader from '@/components/AppHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Plus } from '@element-plus/icons-vue'

export default {
  name: 'EvaluationRecordDetail',
  components: {
    AppHeader,
    ArrowLeft,
    Plus
  },
  props: {
    personnel: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      loading: false,
      saving: false,
      personnelInfo: {
        personnel: '',
        department_name: '',
        grade: '',
        total_bonus: 0,
        total_deduction: 0,
        bonus_count: 0,
        deduction_count: 0
      },
      records: [],
      dialogVisible: false,
      isEditing: false,
      currentRecordId: null,
      form: this.getEmptyForm(),
      formRules: {
        item_description: [
          { required: true, message: '请输入扣分/加分说明', trigger: 'blur' },
          { min: 1, max: 255, message: '长度在 1 到 255 个字符', trigger: 'blur' }
        ],
        evaluation_date: [{ required: true, message: '请选择考评时间', trigger: 'change' }],
        score: [{ required: true, message: '请输入分值', trigger: 'blur' }]
      }
    }
  },
  async mounted() {
    await this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        // 从路由参数或props获取人员姓名，确保正确解码
        let personnelName = this.personnel
        if (!personnelName && this.$route.params.personnel) {
          const paramValue = this.$route.params.personnel
          try {
            // 先尝试解码（处理URL编码的情况）
            personnelName = decodeURIComponent(paramValue)
          } catch (e) {
            // 如果解码失败，可能是已经被解码过了或者是其他格式，直接使用
            personnelName = paramValue
          }
          // 如果解码后还是编码格式（包含%），再次尝试解码
          if (personnelName.includes('%')) {
            try {
              personnelName = decodeURIComponent(personnelName)
            } catch (e2) {
              // 忽略解码错误
            }
          }
        }
        if (!personnelName) {
          personnelName = ''
        }
        const department = this.$route.query.department || ''
        const grade = this.$route.query.grade || ''

        // 获取人员信息和记录
        const [summaryResp, recordsResp] = await Promise.all([
          evaluationService.getPersonnelSummary({ personnel: personnelName }),
          evaluationService.getPersonnelRecords(personnelName)
        ])

        if (summaryResp.data && summaryResp.data.length > 0) {
          this.personnelInfo = summaryResp.data[0]
          // 确保personnel字段是正确的（后端返回的应该是正确的）
          if (this.personnelInfo.personnel && this.personnelInfo.personnel.includes('%')) {
            try {
              this.personnelInfo.personnel = decodeURIComponent(this.personnelInfo.personnel)
            } catch (e) {
              // 忽略解码错误
            }
          }
        } else {
          this.personnelInfo = {
            personnel: personnelName, // 此时personnelName应该已经是解码后的
            department_name: department,
            grade: grade,
            total_bonus: 0,
            total_deduction: 0,
            bonus_count: 0,
            deduction_count: 0
          }
        }

        this.records = recordsResp.data || []
      } catch (error) {
        console.error('获取数据失败:', error)
        ElMessage.error('加载数据失败')
      } finally {
        this.loading = false
      }
    },
    getEmptyForm() {
      const today = new Date().toISOString().slice(0, 10)
      return {
        item_description: '',
        evaluation_date: today,
        score: 0,
        remarks: ''
      }
    },
    openCreateDialog() {
      this.isEditing = false
      this.currentRecordId = null
      this.form = this.getEmptyForm()
      this.dialogVisible = true
    },
    openEditDialog(record) {
      this.isEditing = true
      this.currentRecordId = record.id
      const score = Number(record.bonus_score || 0) > 0 
        ? Number(record.bonus_score) 
        : -Number(record.deduction_score || 0)
      this.form = {
        item_description: record.item_description,
        evaluation_date: record.evaluation_date,
        score: score,
        remarks: record.remarks || ''
      }
      this.dialogVisible = true
    },
    async handleSubmit() {
      this.$refs.recordFormRef.validate(async valid => {
        if (!valid) return

        this.saving = true
        try {
          const personnelName = this.personnelInfo.personnel
          const score = Number(this.form.score) || 0
          
          // 获取部门ID
          const departmentId = await this.getDepartmentId()
          if (!departmentId) {
            ElMessage.error('无法找到部门，请确保人员信息中包含有效的部门名称')
            this.saving = false
            return
          }

          const payload = {
            department: departmentId,
            personnel: personnelName,
            grade: this.personnelInfo.grade || '',
            item_description: this.form.item_description,
            bonus_score: score > 0 ? score : 0,
            deduction_score: score < 0 ? Math.abs(score) : 0,
            evaluation_date: this.form.evaluation_date,
            remarks: this.form.remarks || ''
          }

          if (this.isEditing && this.currentRecordId) {
            await evaluationService.updateEvaluationRecord(this.currentRecordId, payload)
            ElMessage.success('更新成功')
          } else {
            await evaluationService.createEvaluationRecord(payload)
            ElMessage.success('创建成功')
          }
          this.dialogVisible = false
          await this.fetchData()
        } catch (error) {
          console.error('保存失败:', error)
          const errorMsg = error.response?.data?.detail || error.response?.data?.department?.[0] || '保存失败'
          ElMessage.error(errorMsg)
        } finally {
          this.saving = false
        }
      })
    },
    async confirmDelete(record) {
      try {
        await ElMessageBox.confirm(
          `确定要删除这条记录吗？`,
          '删除确认',
          {
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        await evaluationService.deleteEvaluationRecord(record.id)
        ElMessage.success('删除成功')
        await this.fetchData()
      } catch (error) {
        if (error !== 'cancel' && error !== 'close') {
          console.error('删除失败:', error)
          ElMessage.error('删除失败')
        }
      }
    },
    async getDepartmentId() {
      // 根据部门名称查找部门ID
      try {
        const resp = await financeService.getAllDepartments()
        const dept = resp.data.find(d => d.name === this.personnelInfo.department_name)
        return dept ? dept.id : null
      } catch (error) {
        console.error('获取部门ID失败:', error)
        return null
      }
    },
    formatScore(record) {
      if (record.bonus_score > 0) {
        return `+${Number(record.bonus_score).toFixed(2)}`
      } else if (record.deduction_score > 0) {
        return `-${Number(record.deduction_score).toFixed(2)}`
      }
      return '0.00'
    },
    getScoreClass(record) {
      if (record.bonus_score > 0) {
        return 'bonus-text'
      } else if (record.deduction_score > 0) {
        return 'deduction-text'
      }
      return ''
    },
    formatNumber(value) {
      const num = Number(value || 0)
      return num.toFixed(2)
    }
  }
}
</script>

<style scoped>
.detail-container {
  margin: 20px auto;
  padding: 0 20px;
  max-width: 1200px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
}

.info-section,
.statistics-section,
.records-section {
  margin-bottom: 30px;
}

.info-section h3,
.statistics-section h3,
.records-section h3 {
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  margin: 0;
}

.bonus-text {
  color: #67c23a;
  font-weight: 600;
}

.deduction-text {
  color: #f56c6c;
  font-weight: 600;
}

.dialog-footer {
  text-align: right;
}

@media (max-width: 768px) {
  .detail-container {
    padding: 0 10px;
  }
}
</style>

