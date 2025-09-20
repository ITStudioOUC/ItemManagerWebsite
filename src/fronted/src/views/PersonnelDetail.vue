<template>
  <div class="personnel-detail">
    <el-descriptions :column="2" border>
      <el-descriptions-item label="姓名">
        <el-tag type="primary" size="large">{{ personnel.name }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="学号">{{ personnel.student_id }}</el-descriptions-item>
      <el-descriptions-item label="性别">{{ personnel.gender_display }}</el-descriptions-item>
      <el-descriptions-item label="年级专业">{{ personnel.grade_major }}</el-descriptions-item>
      <el-descriptions-item label="所属部门">
        <el-tag>{{ personnel.department_name }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="项目组">
        {{ personnel.project_group_name || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="职位">
        <el-tag type="warning">{{ personnel.position }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="在职状态">
        <el-tag :type="personnel.is_active ? 'success' : 'danger'">
          {{ personnel.is_active ? '在职' : '已卸任' }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="任职开始时间">{{ personnel.start_date }}</el-descriptions-item>
      <el-descriptions-item label="任职结束时间">{{ personnel.end_date || '-' }}</el-descriptions-item>
    </el-descriptions>

    <el-divider content-position="left">联系方式</el-divider>
    <el-descriptions :column="1" border>
      <el-descriptions-item label="手机号">
        <el-text tag="a" :href="'tel:' + personnel.phone">{{ personnel.phone }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="QQ号">
        <el-text tag="a" :href="'tencent://message/?uin=' + personnel.qq">{{ personnel.qq }}</el-text>
      </el-descriptions-item>
      <el-descriptions-item label="邮箱">
        <el-text tag="a" :href="'mailto:' + personnel.email">{{ personnel.email }}</el-text>
      </el-descriptions-item>
    </el-descriptions>

    <el-divider content-position="left" v-if="personnel.description">备注信息</el-divider>
    <el-card v-if="personnel.description" shadow="never" class="description-card">
      <p>{{ personnel.description }}</p>
    </el-card>

    <el-divider content-position="left">时间信息</el-divider>
    <el-descriptions :column="1" border>
      <el-descriptions-item label="创建时间">{{ formatDateTime(personnel.created_at) }}</el-descriptions-item>
      <el-descriptions-item label="更新时间">{{ formatDateTime(personnel.updated_at) }}</el-descriptions-item>
    </el-descriptions>

    <div class="detail-actions">
      <el-button @click="$emit('close')">关闭</el-button>
    </div>
  </div>
</template>

<script>
import moment from 'moment'

export default {
  name: 'PersonnelDetail',
  props: {
    personnel: {
      type: Object,
      required: true
    }
  },
  emits: ['close'],
  methods: {
    formatDateTime(dateTime) {
      return moment(dateTime).format('YYYY-MM-DD HH:mm:ss')
    }
  }
}
</script>

<style scoped>
.personnel-detail {
  padding: 20px 0;
}

.description-card {
  margin: 10px 0;
  background-color: #f8f9fa;
}

.description-card p {
  margin: 0;
  line-height: 1.6;
}

.detail-actions {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

:deep(.el-descriptions__label) {
  font-weight: bold;
}
</style>
