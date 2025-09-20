<template>
  <AppHeader />
  <div class="item-list">
    <div class="toolbar">
      <el-button type="primary" @click="showAddDialog = true">
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
          <el-button size="small" @click="editItem(scope.row)">
            编辑
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加物品对话框 -->
    <el-dialog v-model="showAddDialog" title="添加物品" width="600px">
      <el-form :model="newItem" label-width="100px" :rules="itemRules" ref="itemForm">
        <el-form-item label="物品名称" prop="name">
          <el-input v-model="newItem.name" />
        </el-form-item>
        <el-form-item label="序列号" prop="serial_number">
          <el-input v-model="newItem.serial_number" />
        </el-form-item>
        <el-form-item label="类别" prop="category">
          <el-input v-model="newItem.category" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input type="textarea" v-model="newItem.description" />
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="newItem.location" />
        </el-form-item>
        <el-form-item label="价值">
          <el-input-number v-model="newItem.value" :precision="2" :min="0" />
        </el-form-item>
        <el-form-item label="购买日期">
          <el-date-picker v-model="newItem.purchase_date" type="date" />
        </el-form-item>
        <el-form-item label="所有者">
          <el-input v-model="newItem.owner" placeholder="请输入所有者姓名" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveItem">保存</el-button>
      </template>
    </el-dialog>

    <!-- 借用物品对话框 -->
    <el-dialog v-model="showBorrowDialog" title="借用物品" width="500px">
      <el-form :model="borrowForm" :rules="borrowRules" ref="borrowForm" label-width="100px">
        <el-form-item label="使用者" prop="user_name">
          <el-input v-model="borrowForm.user_name" placeholder="请输入使用者姓名" />
        </el-form-item>
        <el-form-item label="联系方式" prop="user_contact">
          <el-input v-model="borrowForm.user_contact" placeholder="请输入联系方式（手机号/QQ/微信/邮箱等）" />
        </el-form-item>
        <el-form-item label="使用目的">
          <el-input v-model="borrowForm.purpose" />
        </el-form-item>
        <el-form-item label="使用前状况">
          <el-input v-model="borrowForm.condition_before" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input type="textarea" v-model="borrowForm.notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBorrowDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmBorrow">确认借用</el-button>
      </template>
    </el-dialog>

    <!-- 归还物品对话框 -->
    <el-dialog v-model="showReturnDialog" title="归还物品" width="500px">
      <el-form :model="returnForm" :rules="returnRules" ref="returnForm" label-width="100px">
        <el-form-item label="使用后状况" prop="condition_after">
          <el-input v-model="returnForm.condition_after" placeholder="请描述物品使用后的状况" />
        </el-form-item>
        <el-form-item label="归还备注">
          <el-input type="textarea" v-model="returnForm.return_notes" placeholder="可填写其他归还说明（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReturnDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmReturn">确认归还</el-button>
      </template>
    </el-dialog>

    <!-- 编辑物品对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑物品" width="600px">
      <el-form :model="editForm" label-width="100px" :rules="itemRules" ref="editForm">
        <el-form-item label="物品名称" prop="name">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="序列号" prop="serial_number">
          <el-input v-model="editForm.serial_number" />
        </el-form-item>
        <el-form-item label="类别" prop="category">
          <el-input v-model="editForm.category" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status">
            <el-option label="可用" value="available" />
            <el-option label="使用中" value="in_use" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="损坏" value="damaged" />
            <el-option label="丢失" value="lost" />
            <el-option label="已弃用" value="abandoned" />
            <el-option label="禁止借用" value="prohibited" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input type="textarea" v-model="editForm.description" />
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="editForm.location" />
        </el-form-item>
        <el-form-item label="价值">
          <el-input-number v-model="editForm.value" :precision="2" :min="0" />
        </el-form-item>
        <el-form-item label="购买日期">
          <el-date-picker v-model="editForm.purchase_date" type="date" />
        </el-form-item>
        <el-form-item label="所有者" prop="owner_id">
          <el-input v-model="editForm.owner" placeholder="请输入所有者姓名" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updateItem">保存修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import {itemService, userService} from '../services/api'
import {ElMessage} from 'element-plus'
import AppHeader from '../components/AppHeader.vue'

export default {
  name: 'ItemList',
  components: {
    AppHeader
  },
  data() {
    return {
      items: [],
      users: [],
      loading: false,
      searchKeyword: '',
      statusFilter: '',
      showAddDialog: false,
      showBorrowDialog: false,
      showReturnDialog: false,
      showEditDialog: false,
      currentItem: null,
      newItem: {
        name: '',
        serial_number: '',
        category: '',
        description: '',
        location: '',
        value: null,
        purchase_date: null,
        owner: ''
      },
      borrowForm: {
        user_name: '',
        user_contact: '',
        purpose: '',
        condition_before: '',
        notes: ''
      },
      returnForm: {
        condition_after: '',
        return_notes: ''
      },
      editForm: {
        id: null,
        name: '',
        serial_number: '',
        category: '',
        status: '',
        description: '',
        location: '',
        value: null,
        purchase_date: null,
        owner: ''
      },
      itemRules: {
        name: [{ required: true, message: '请输入物品名称', trigger: 'blur' }],
        serial_number: [{ required: true, message: '请输入序列号', trigger: 'blur' }],
        category: [{ required: true, message: '请输入类别', trigger: 'blur' }]
      },
      returnRules: {
        condition_after: [{ required: true, message: '请输入使用后状况', trigger: 'blur' }]
      },
      borrowRules: {
        user_name: [{ required: true, message: '请输入使用者姓名', trigger: 'blur' }],
        user_contact: [{ required: true, message: '请输入联系方式', trigger: 'blur' }]
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
    await this.loadUsers()
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
    async loadUsers() {
      try {
        const response = await userService.getAllUsers()
        this.users = response.data
      } catch (error) {
        console.error('加载用户列表失败:', error)
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
    editItem(item) {
      this.currentItem = item
      this.editForm = { ...item }
      this.showEditDialog = true
    },
    borrowItem(item) {
      this.currentItem = item
      this.borrowForm = {
        user_name: '',
        user_contact: '',
        purpose: '',
        condition_before: '',
        notes: ''
      }
      this.showBorrowDialog = true
    },
    returnItem(item) {
      this.currentItem = item
      this.returnForm = {
        condition_after: '',
        return_notes: ''
      }
      this.showReturnDialog = true
    },
    async saveItem() {
      try {
        await this.$refs.itemForm.validate()

        const itemData = { ...this.newItem }

        // 格式化购买日期
        if (itemData.purchase_date) {
          const date = new Date(itemData.purchase_date)
          itemData.purchase_date = date.getFullYear() + '-' +
            String(date.getMonth() + 1).padStart(2, '0') + '-' +
            String(date.getDate()).padStart(2, '0')
        }

        await itemService.createItem(itemData)
        ElMessage.success('物品添加成功')
        this.showAddDialog = false
        this.newItem = {
          name: '',
          serial_number: '',
          category: '',
          description: '',
          location: '',
          value: null,
          purchase_date: null,
          owner: ''
        }
        await this.loadItems()
      } catch (error) {
        console.error('添加物品失败:', error)
        ElMessage.error('添加物品失败')
      }
    },
    async confirmBorrow() {
      try {
        await this.$refs.borrowForm.validate()

        await itemService.borrowItem(this.currentItem.id, this.borrowForm)
        ElMessage.success('借用成功')
        this.showBorrowDialog = false
        await this.loadItems()
      } catch (error) {
        if (error.message && error.message.includes('validation')) {
          return
        }
        console.error('借用失败:', error)
        ElMessage.error('借用失败')
      }
    },
    async confirmReturn() {
      try {
        await this.$refs.returnForm.validate()

        await itemService.returnItem(this.currentItem.id, this.returnForm)
        ElMessage.success('归还成功')
        this.showReturnDialog = false
        await this.loadItems()
      } catch (error) {
        if (error.message && error.message.includes('validation')) {
          return
        }
        console.error('归还失败:', error)
        ElMessage.error('归还失败')
      }
    },
    async updateItem() {
      try {
        await this.$refs.editForm.validate()

        const itemData = { ...this.editForm }

        // 格式化购买日期
        if (itemData.purchase_date) {
          const date = new Date(itemData.purchase_date)
          itemData.purchase_date = date.getFullYear() + '-' +
            String(date.getMonth() + 1).padStart(2, '0') + '-' +
            String(date.getDate()).padStart(2, '0')
        }

        await itemService.updateItem(itemData.id, itemData)
        ElMessage.success('物品信息更新成功')
        this.showEditDialog = false
        await this.loadItems()
      } catch (error) {
        console.error('更新物品失败:', error)
        ElMessage.error('更新物品失败')
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
</style>
