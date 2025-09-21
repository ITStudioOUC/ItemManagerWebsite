<template>
  <AppHeader />
  <div class="item-list">
    <div class="toolbar">
      <el-button type="primary" @click="$router.push('/items/create')">
        <el-icon><Plus /></el-icon>
        添加物品
      </el-button>
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索物品名称或序列号"
          style="width: 300px;"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="statusFilter" placeholder="状态筛选" style="margin-left: 10px;" @change="handleFilter">
          <el-option label="全部" value="" />
          <el-option label="可用" value="available" />
          <el-option label="使用中" value="in_use" />
          <el-option label="维护中" value="maintenance" />
          <el-option label="损坏" value="damaged" />
          <el-option label="丢失" value="lost" />
          <el-option label="已弃用" value="abandoned" />
          <el-option label="禁止借用" value="prohibited" />
        </el-select>
      </div>
    </div>

    <el-table :data="filteredItems" style="width: 100%" v-loading="loading">
      <el-table-column label="图片" width="80">
        <template #default="scope">
          <el-image
            v-if="scope.row.primary_image"
            :src="scope.row.primary_image"
            fit="cover"
            style="width: 50px; height: 50px; border-radius: 4px; cursor: pointer;"
            :preview-src-list="[scope.row.primary_image]"
            preview-teleported
          />
          <el-image
            v-else-if="scope.row.images && scope.row.images.length > 0"
            :src="scope.row.images[0].image_url"
            fit="cover"
            style="width: 50px; height: 50px; border-radius: 4px; cursor: pointer;"
            :preview-src-list="[scope.row.images[0].image_url]"
            preview-teleported
          />
          <div v-else class="no-image-placeholder">
            <el-icon><Picture /></el-icon>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="物品名称" />
      <el-table-column prop="serial_number" label="序列号" />
      <el-table-column prop="category" label="类别" />
      <el-table-column prop="status" label="状态">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="owner" label="所有者">
        <template #default="scope">
          <span v-if="scope.row.owner">
            {{ scope.row.owner }}
          </span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="current_user" label="当前使用者">
        <template #default="scope">
          <span v-if="scope.row.current_user">
            {{ scope.row.current_user.username }}
          </span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="location" label="位置" />
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button size="small" @click="viewItem(scope.row.id)">
            详情
          </el-button>
          <el-button
            v-if="scope.row.status === 'available'"
            size="small"
            type="warning"
            @click="borrowItem(scope.row)"
          >
            借用
          </el-button>
          <el-button
            v-if="scope.row.status === 'in_use'"
            size="small"
            type="success"
            @click="returnItem(scope.row)"
          >
            归还
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 借用物品对话框 -->
    <el-dialog v-model="showBorrowDialog" title="借用物品" width="600px">
      <div v-if="selectedItem">
        <h4>{{ selectedItem.name }} ({{ selectedItem.serial_number }})</h4>
        <el-form :model="borrowForm" :rules="borrowRules" ref="borrowFormRef" label-width="120px">
          <el-form-item label="借用人姓名" prop="user_name">
            <el-input v-model="borrowForm.user_name" placeholder="请输入借用人姓名" />
          </el-form-item>
          <el-form-item label="联系方式" prop="user_contact">
            <el-input v-model="borrowForm.user_contact" placeholder="请输入联系方式" />
          </el-form-item>
          <el-form-item label="使用目的" prop="purpose">
            <el-input v-model="borrowForm.purpose" placeholder="请输入使用目的" />
          </el-form-item>
          <el-form-item label="预计归还时间">
            <el-date-picker
              v-model="borrowForm.expected_return_time"
              type="datetime"
              placeholder="请选择预计归还时间"
              format="YYYY-MM-DD HH:mm"
              value-format="YYYY-MM-DD HH:mm:ss"
            />
          </el-form-item>
          <el-form-item label="使用前状况">
            <el-input v-model="borrowForm.condition_before" type="textarea" :rows="2" placeholder="请描述物品当前状况" />
          </el-form-item>
          <el-form-item label="借用时图片">
            <el-upload
              ref="borrowUploadRef"
              :auto-upload="false"
              :multiple="true"
              :limit="5"
              accept="image/*"
              list-type="picture-card"
              :on-change="handleBorrowImageChange"
              :on-remove="handleBorrowImageRemove"
            >
              <el-icon><Plus /></el-icon>
            </el-upload>
            <div style="margin-top: 5px;">
              <el-text type="info" size="small">
                可上传借用时的物品状态图片（可选，最多5张）
              </el-text>
            </div>
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="borrowForm.notes" type="textarea" :rows="3" placeholder="其他备注信息" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showBorrowDialog = false">取消</el-button>
          <el-button type="primary" @click="confirmBorrow" :loading="borrowing">
            确认借用
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 归还物品对话框 -->
    <el-dialog v-model="showReturnDialog" title="归还物品" width="600px">
      <div v-if="selectedItem">
        <h4>{{ selectedItem.name }} ({{ selectedItem.serial_number }})</h4>
        <el-form :model="returnForm" ref="returnFormRef" label-width="120px">
          <el-form-item label="使用后状况">
            <el-input v-model="returnForm.condition_after" type="textarea" :rows="2" placeholder="请描述物品归还时的状况" />
          </el-form-item>
          <el-form-item label="归还时图片">
            <el-upload
              ref="returnUploadRef"
              :auto-upload="false"
              :multiple="true"
              :limit="5"
              accept="image/*"
              list-type="picture-card"
              :on-change="handleReturnImageChange"
              :on-remove="handleReturnImageRemove"
            >
              <el-icon><Plus /></el-icon>
            </el-upload>
            <div style="margin-top: 5px;">
              <el-text type="info" size="small">
                可上传归还时的物品状态图片（可选，最多5张）
              </el-text>
            </div>
          </el-form-item>
          <el-form-item label="归还备注">
            <el-input v-model="returnForm.return_notes" type="textarea" :rows="3" placeholder="归还时的备注信息" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showReturnDialog = false">取消</el-button>
          <el-button type="primary" @click="confirmReturn" :loading="returning">
            确认归还
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import {itemService} from '@/services/api'
import {ElMessage} from 'element-plus'
import AppHeader from '../components/AppHeader.vue'
import { Plus, Search, Picture } from '@element-plus/icons-vue'

export default {
  name: 'ItemList',
  components: {
    AppHeader,
    Plus,
    Search,
    Picture
  },
  data() {
    return {
      items: [],
      loading: false,
      searchKeyword: '',
      statusFilter: '',
      showBorrowDialog: false,
      showReturnDialog: false,
      selectedItem: null,
      borrowing: false,
      returning: false,
      borrowFiles: [],
      returnFiles: [],
      borrowForm: {
        user_name: '',
        user_contact: '',
        purpose: '',
        expected_return_time: null,
        condition_before: '',
        notes: ''
      },
      returnForm: {
        condition_after: '',
        return_notes: ''
      },
      borrowRules: {
        user_name: [
          { required: true, message: '请输入借用人姓名', trigger: 'blur' }
        ],
        user_contact: [
          { required: true, message: '请输入联系方式', trigger: 'blur' }
        ],
        purpose: [
          { required: true, message: '请输入使用目的', trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    filteredItems() {
      let filtered = this.items

      if (this.searchKeyword) {
        filtered = filtered.filter(item =>
          item.name.toLowerCase().includes(this.searchKeyword.toLowerCase()) ||
          item.serial_number.toLowerCase().includes(this.searchKeyword.toLowerCase())
        )
      }

      if (this.statusFilter) {
        filtered = filtered.filter(item => item.status === this.statusFilter)
      }

      return filtered
    }
  },
  async mounted() {
    await this.loadItems()
  },
  methods: {
    async loadItems() {
      this.loading = true
      try {
        const response = await itemService.getAllItems()
        this.items = response.data
      } catch (error) {
        console.error('加载物品列表失败:', error)
        ElMessage.error('加载物品列表失败')
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      // 搜索逻辑在computed中处理
    },
    handleFilter() {
      // 筛选逻辑在computed中处理
    },
    viewItem(id) {
      this.$router.push(`/items/${id}`)
    },
    borrowItem(item) {
      this.selectedItem = item
      this.borrowForm = {
        user_name: '',
        user_contact: '',
        purpose: '',
        expected_return_time: null,
        condition_before: '',
        notes: ''
      }
      this.showBorrowDialog = true
    },
    returnItem(item) {
      this.selectedItem = item
      this.returnForm = {
        condition_after: '',
        return_notes: ''
      }
      this.showReturnDialog = true
    },
    async confirmBorrow() {
      try {
        await this.$refs.borrowFormRef.validate()

        this.borrowing = true

        // 创建FormData对象
        const formData = new FormData()

        // 添加表单数据
        Object.keys(this.borrowForm).forEach(key => {
          if (this.borrowForm[key] !== null && this.borrowForm[key] !== '') {
            formData.append(key, this.borrowForm[key])
          }
        })

        // 添加借用时图片
        this.borrowFiles.forEach((file, index) => {
          formData.append('borrow_images', file)
          formData.append(`borrow_image_descriptions[${index}]`, '')
        })

        await itemService.borrowItem(this.selectedItem.id, formData)
        ElMessage.success('借用成功')
        this.showBorrowDialog = false
        this.borrowFiles = []
        this.$refs.borrowUploadRef?.clearFiles()
        await this.loadItems()
      } catch (error) {
        if (error.message && error.message.includes('validation')) {
          return
        }
        console.error('借用失败:', error)
        ElMessage.error(error.response?.data?.error || '借用失败')
      } finally {
        this.borrowing = false
      }
    },
    async confirmReturn() {
      try {
        this.returning = true

        // 创建FormData对象
        const formData = new FormData()

        // 添加表单数据
        Object.keys(this.returnForm).forEach(key => {
          if (this.returnForm[key] !== null && this.returnForm[key] !== '') {
            formData.append(key, this.returnForm[key])
          }
        })

        // 添加归还时图片
        this.returnFiles.forEach((file, index) => {
          formData.append('return_images', file)
          formData.append(`return_image_descriptions[${index}]`, '')
        })

        await itemService.returnItem(this.selectedItem.id, formData)
        ElMessage.success('归还成功')
        this.showReturnDialog = false
        this.returnFiles = []
        this.$refs.returnUploadRef?.clearFiles()
        await this.loadItems()
      } catch (error) {
        console.error('归还失败:', error)
        ElMessage.error(error.response?.data?.error || '归还失败')
      } finally {
        this.returning = false
      }
    },
    getStatusType(status) {
      const typeMap = {
        'available': 'success',
        'in_use': 'warning',
        'maintenance': 'info',
        'damaged': 'danger',
        'lost': 'danger',
        'abandoned': 'info',
        'prohibited': 'warning'
      }
      return typeMap[status] || 'info'
    },
    getStatusText(status) {
      const textMap = {
        'available': '可用',
        'in_use': '使用中',
        'maintenance': '维护中',
        'damaged': '损坏',
        'lost': '丢失',
        'abandoned': '已弃用',
        'prohibited': '禁止借用'
      }
      return textMap[status] || '未知'
    },
    handleBorrowImageChange(file, fileList) {
      this.borrowFiles = fileList.map(file => file.raw)
    },
    handleBorrowImageRemove(file, fileList) {
      this.borrowFiles = fileList.map(file => file.raw)
    },
    handleReturnImageChange(file, fileList) {
      this.returnFiles = fileList.map(file => file.raw)
    },
    handleReturnImageRemove(file, fileList) {
      this.returnFiles = fileList.map(file => file.raw)
    }
  }
}
</script>

<style scoped>
.item-list {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-bar {
  display: flex;
  align-items: center;
}

.no-image-placeholder {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  background-color: #f5f7fa;
  color: #909399;
}
</style>
