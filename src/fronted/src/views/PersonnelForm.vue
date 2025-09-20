<template>
  <el-form :model="form" :rules="rules" ref="personnelForm" label-width="120px">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="学号" prop="student_id">
          <el-input v-model="form.student_id" placeholder="请输入学号" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="性别" prop="gender">
          <el-select v-model="form.gender" placeholder="请选择性别">
            <el-option label="男" value="male" />
            <el-option label="女" value="female" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="年级专业" prop="grade_major">
          <el-input v-model="form.grade_major" placeholder="如：2023级计算机科学与技术" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="所属部门" prop="department">
          <el-select v-model="form.department" placeholder="请选择部门" @change="onDepartmentChange">
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="项目组" prop="project_group">
          <el-select v-model="form.project_group" placeholder="请选择项目组（可选）" clearable>
            <el-option
              v-for="group in filteredProjectGroups"
              :key="group.id"
              :label="group.name"
              :value="group.id" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="职位" prop="position">
          <el-input v-model="form.position" placeholder="请输入职位" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="在职状态" prop="is_active">
          <el-switch
            v-model="form.is_active"
            active-text="在职"
            inactive-text="已卸任" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="任职开始时间" prop="start_date">
          <el-date-picker
            v-model="form.start_date"
            type="date"
            placeholder="选择任职开始时间"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="任职结束时间" prop="end_date">
          <el-date-picker
            v-model="form.end_date"
            type="date"
            placeholder="选择任职结束时间（可选）"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            clearable />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="QQ号" prop="qq">
          <el-input v-model="form.qq" placeholder="请输入QQ号" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-form-item label="备注信息" prop="description">
      <el-input
        v-model="form.description"
        type="textarea"
        :rows="3"
        placeholder="请输入备注信息（可选）" />
    </el-form-item>

    <div class="form-actions">
      <el-button @click="$emit('cancel')">取消</el-button>
      <el-button type="primary" @click="submitForm">保存</el-button>
    </div>
  </el-form>
</template>

<script>
import { personnelService } from '@/services/api'

export default {
  name: 'PersonnelForm',
  props: {
    personnel: {
      type: Object,
      default: null
    },
    departments: {
      type: Array,
      default: () => []
    },
    projectGroups: {
      type: Array,
      default: () => []
    }
  },
  emits: ['submit', 'cancel'],
  data() {
    return {
      form: {
        name: '',
        student_id: '',
        gender: '',
        grade_major: '',
        department: '',
        project_group: '',
        position: '',
        start_date: '',
        end_date: '',
        is_active: true,
        phone: '',
        qq: '',
        email: '',
        description: ''
      },
      rules: {
        name: [
          { required: true, message: '请输入姓名', trigger: 'blur' }
        ],
        student_id: [
          { required: true, message: '请输入学号', trigger: 'blur' },
          { pattern: /^\d{11}$/, message: '学号应为11位数字', trigger: 'blur' }
        ],
        gender: [
          { required: true, message: '请选择性别', trigger: 'change' }
        ],
        grade_major: [
          { required: true, message: '请输入年级专业', trigger: 'blur' }
        ],
        department: [
          { required: true, message: '请选择所属部门', trigger: 'change' }
        ],
        position: [
          { required: true, message: '请选择职位', trigger: 'change' }
        ],
        start_date: [
          { required: true, message: '请选择任职开始时间', trigger: 'change' }
        ],
        phone: [
          { required: true, message: '请输入手机号', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号码', trigger: 'blur' }
        ],
        qq: [
          { required: true, message: '请输入QQ号', trigger: 'blur' },
          { pattern: /^\d{5,15}$/, message: 'QQ号应为5-15位数字', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    filteredProjectGroups() {
      if (!this.form.department) {
        return []
      }
      const departmentId = parseInt(this.form.department)
      return this.projectGroups.filter(group => group.department === departmentId)
    }
  },
  watch: {
    personnel: {
      handler(newVal) {
        if (newVal) {
          this.form = { ...newVal }
        } else {
          this.resetForm()
        }
      },
      immediate: true
    }
  },
  methods: {
    onDepartmentChange() {
      // 部门变更时清空项目组选择
      this.form.project_group = ''
    },

    resetForm() {
      this.form = {
        name: '',
        student_id: '',
        gender: '',
        grade_major: '',
        department: '',
        project_group: '',
        position: '',
        start_date: '',
        end_date: '',
        is_active: true,
        phone: '',
        qq: '',
        email: '',
        description: ''
      }
    },

    async submitForm() {
      try {
        await this.$refs.personnelForm.validate()

        // 验证结束时间
        if (this.form.end_date && this.form.start_date >= this.form.end_date) {
          this.$message.error('任职结束时间必须晚于开始时间')
          return
        }

        const formData = { ...this.form }

        // 如果没有选择项目组，设为null
        if (!formData.project_group) {
          formData.project_group = null
        }

        // 如果没有结束时间，设为null
        if (!formData.end_date) {
          formData.end_date = null
        }

        if (this.personnel && this.personnel.id) {
          // 更新人员信息
          await personnelService.updatePersonnel(this.personnel.id, formData)
          this.$message.success('人员信息更新成功')
        } else {
          // 创建新人员
          await personnelService.createPersonnel(formData)
          this.$message.success('人员添加成功')
        }

        this.$emit('submit')
      } catch (error) {
        if (error.response && error.response.data) {
          // 处理后端验证错误
          const errors = error.response.data
          for (const field in errors) {
            if (errors[field] && Array.isArray(errors[field])) {
              this.$message.error(`${field}: ${errors[field][0]}`)
            }
          }
        } else {
          this.$message.error('操作失败，请重试')
        }
        console.error('提交人员信息失败:', error)
      }
    }
  }
}
</script>

<style scoped>
.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}
</style>
