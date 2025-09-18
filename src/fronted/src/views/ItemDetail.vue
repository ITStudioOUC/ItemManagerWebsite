<template>
  <el-header>
    <div class="header-content">
      <h1 class="logo">爱特工作室物品管理系统</h1>
      <el-menu
          mode="horizontal"
          :default-active="$route.path"
          router
          class="nav-menu"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          首页
        </el-menu-item>
        <el-menu-item index="/items">
          <el-icon><Box /></el-icon>
          物品管理
        </el-menu-item>
        <el-menu-item index="/usage">
          <el-icon><Document /></el-icon>
          使用记录
        </el-menu-item>
      </el-menu>
    </div>
  </el-header>
  <div class="item-detail">
    <div class="detail-header">
      <el-button @click="$router.go(-1)" style="margin-bottom: 20px;">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
    </div>

    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>物品详情</span>
          <el-button type="primary" @click="editMode = !editMode">
            {{ editMode ? '取消编辑' : '编辑' }}
          </el-button>
        </div>
      </template>

      <div v-if="item">
        <el-form :model="editableItem" label-width="120px" :disabled="!editMode">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="物品名称">
                <el-input v-model="editableItem.name" />
              </el-form-item>
              <el-form-item label="序列号">
                <el-input v-model="editableItem.serial_number" />
              </el-form-item>
              <el-form-item label="类别">
                <el-input v-model="editableItem.category" />
              </el-form-item>
              <el-form-item label="状态">
                <el-select v-model="editableItem.status">
                  <el-option label="可用" value="available" />
                  <el-option label="使用中" value="in_use" />
                  <el-option label="维护中" value="maintenance" />
                  <el-option label="损坏" value="damaged" />
                </el-select>
              </el-form-item>
              <el-form-item label="位置">
                <el-input v-model="editableItem.location" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="购买日期">
                <el-date-picker v-model="editableItem.purchase_date" type="date" />
              </el-form-item>
              <el-form-item label="价值">
                <el-input-number v-model="editableItem.value" :precision="2" :min="0" />
              </el-form-item>
              <el-form-item label="创建时间">
                <el-input :value="formatDate(item.created_at)" disabled />
              </el-form-item>
              <el-form-item label="更新时间">
                <el-input :value="formatDate(item.updated_at)" disabled />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="描述">
            <el-input type="textarea" v-model="editableItem.description" :rows="3" />
          </el-form-item>
        </el-form>

        <div v-if="editMode" style="text-align: center; margin-top: 20px;">
          <el-button @click="editMode = false">取消</el-button>
          <el-button type="primary" @click="saveChanges">保存修改</el-button>
        </div>

        <!-- 当前使用者信息 -->
        <el-card v-if="item.current_user" style="margin-top: 20px;">
          <template #header>
            <span>当前使用者</span>
          </template>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="使用者">{{ item.current_user.username }}</el-descriptions-item>
            <el-descriptions-item label="姓名">{{ item.current_user.first_name }} {{ item.current_user.last_name }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ item.current_user.email }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 使用历史 -->
        <el-card style="margin-top: 20px;">
          <template #header>
            <span>使用历史</span>
          </template>
          <el-table :data="item.usage_history" style="width: 100%">
            <el-table-column prop="user.username" label="使用者" />
            <el-table-column prop="start_time" label="开始时间">
              <template #default="scope">
                {{ formatDate(scope.row.start_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="end_time" label="结束时间">
              <template #default="scope">
                {{ scope.row.end_time ? formatDate(scope.row.end_time) : '使用中' }}
              </template>
            </el-table-column>
            <el-table-column prop="purpose" label="使用目的" />
            <el-table-column prop="is_returned" label="状态">
              <template #default="scope">
                <el-tag :type="scope.row.is_returned ? 'success' : 'warning'">
                  {{ scope.row.is_returned ? '已归还' : '使用中' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button size="small" @click="showUsageDetail(scope.row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </el-card>

    <!-- 使用记录详情对话框 -->
    <el-dialog v-model="showUsageDialog" title="使用记录详情" width="600px">
      <div v-if="selectedUsage">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="使用者">{{ selectedUsage.user.username }}</el-descriptions-item>
          <el-descriptions-item label="使用目的">{{ selectedUsage.purpose }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDate(selectedUsage.start_time) }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ selectedUsage.end_time ? formatDate(selectedUsage.end_time) : '使用中' }}
          </el-descriptions-item>
          <el-descriptions-item label="使用前状况">{{ selectedUsage.condition_before || '无' }}</el-descriptions-item>
          <el-descriptions-item label="使用后状况">{{ selectedUsage.condition_after || '无' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ selectedUsage.notes || '无' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { itemService } from '../services/api'
import { ElMessage } from 'element-plus'
import moment from 'moment'

export default {
  name: 'ItemDetail',
  props: {
    id: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      item: null,
      editableItem: {},
      loading: false,
      editMode: false,
      showUsageDialog: false,
      selectedUsage: null
    }
  },
  async mounted() {
    await this.loadItem()
  },
  methods: {
    async loadItem() {
      this.loading = true
      try {
        const response = await itemService.getItemDetail(this.id)
        this.item = response.data
        this.editableItem = { ...this.item }
      } catch (error) {
        console.error('加载物品详情失败:', error)
        ElMessage.error('加载物品详情失败')
      } finally {
        this.loading = false
      }
    },
    async saveChanges() {
      try {
        await itemService.updateItem(this.id, this.editableItem)
        ElMessage.success('修改保存成功')
        this.editMode = false
        await this.loadItem()
      } catch (error) {
        console.error('保存修改失败:', error)
        ElMessage.error('保存修改失败')
      }
    },
    showUsageDetail(usage) {
      this.selectedUsage = usage
      this.showUsageDialog = true
    },
    formatDate(dateString) {
      return moment(dateString).format('YYYY-MM-DD HH:mm:ss')
    }
  }
}
</script>

<style scoped>
.item-detail {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
