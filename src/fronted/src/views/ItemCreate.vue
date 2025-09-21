<template>
  <AppHeader />
  <div class="item-create">
    <div class="create-header">
      <el-button @click="$router.go(-1)" style="margin-bottom: 20px;">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h2>创建新物品</h2>
    </div>

    <el-card>
      <el-form :model="itemForm" :rules="rules" ref="itemFormRef" label-width="120px">
        <!-- 物品图片上传 - 必填项 -->
        <el-form-item label="物品图片" required>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :multiple="true"
            :limit="10"
            accept="image/*"
            list-type="picture-card"
            :on-change="handleImageChange"
            :on-remove="handleImageRemove"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div style="margin-top: 10px;">
            <el-text type="info" size="small">
              * 必须上传至少一张图片，支持 JPG、PNG 格式，最多上传 10 张图片
            </el-text>
          </div>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="物品名称" prop="name">
              <el-input v-model="itemForm.name" placeholder="请输入物品名称" />
            </el-form-item>

            <el-form-item label="序列号" prop="serial_number">
              <el-input v-model="itemForm.serial_number" placeholder="请输入序列号" />
            </el-form-item>

            <el-form-item label="类别" prop="category">
              <el-select v-model="itemForm.category" placeholder="请选择类别" style="width: 100%">
                <el-option
                  v-for="category in categories"
                  :key="category.id"
                  :label="category.name"
                  :value="category.name"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="位置" prop="location">
              <el-input v-model="itemForm.location" placeholder="请输入存放位置" />
            </el-form-item>

            <el-form-item label="所有者" prop="owner">
              <el-input v-model="itemForm.owner" placeholder="请输入所有者姓名" />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="购买日期" prop="purchase_date">
              <el-date-picker
                v-model="itemForm.purchase_date"
                type="date"
                placeholder="请选择购买日期"
                style="width: 100%"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>

            <el-form-item label="价值" prop="value">
              <el-input-number
                v-model="itemForm.value"
                :precision="2"
                :min="0"
                placeholder="请输入物品价值"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="状态" prop="status">
              <el-select v-model="itemForm.status" placeholder="请选择状态" style="width: 100%">
                <el-option label="可用" value="available" />
                <el-option label="维护中" value="maintenance" />
                <el-option label="损坏" value="damaged" />
                <el-option label="已弃用" value="abandoned" />
                <el-option label="禁止借用" value="prohibited" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="描述" prop="description">
          <el-input
            type="textarea"
            v-model="itemForm.description"
            :rows="4"
            placeholder="请输入物品描述"
          />
        </el-form-item>

        <el-form-item>
          <el-button @click="resetForm">重置</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">
            创建物品
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { itemService, categoryService } from '@/services/api'
import { ElMessage } from 'element-plus'
import AppHeader from '../components/AppHeader.vue'
import { Plus, ArrowLeft } from '@element-plus/icons-vue'

export default {
  name: 'ItemCreate',
  components: {
    AppHeader,
    Plus,
    ArrowLeft
  },
  data() {
    return {
      itemForm: {
        name: '',
        description: '',
        serial_number: '',
        category: '',
        status: 'available',
        location: '',
        owner: '',
        purchase_date: null,
        value: null
      },
      uploadFiles: [],
      categories: [],
      submitting: false,
      rules: {
        name: [
          { required: true, message: '请输入物品名称', trigger: 'blur' }
        ],
        serial_number: [
          { required: true, message: '请输入序列号', trigger: 'blur' }
        ],
        category: [
          { required: true, message: '请选择类别', trigger: 'change' }
        ]
      }
    }
  },
  async mounted() {
    await this.loadCategories()
  },
  methods: {
    async loadCategories() {
      try {
        const response = await categoryService.getAllCategories()
        this.categories = response.data
      } catch (error) {
        console.error('加载类别失败:', error)
        ElMessage.error('加载类别失败')
      }
    },

    handleImageChange(file, fileList) {
      this.uploadFiles = fileList
    },

    handleImageRemove(file, fileList) {
      this.uploadFiles = fileList
    },

    async submitForm() {
      // 首先验证图片是否上传
      if (this.uploadFiles.length === 0) {
        ElMessage.error('请至少上传一张物品图片')
        return
      }

      try {
        // 验证表单
        await this.$refs.itemFormRef.validate()

        this.submitting = true

        // 创建FormData对象
        const formData = new FormData()

        // 添加物品基本信息
        Object.keys(this.itemForm).forEach(key => {
          const value = this.itemForm[key]
          if (value !== null && value !== '' && value !== undefined) {
            formData.append(key, value)
          }
        })

        // 添加图片文件
        this.uploadFiles.forEach((fileItem, index) => {
          // 确保获取正确的文件对象
          const file = fileItem.raw || fileItem
          if (file instanceof File) {
            formData.append('images', file)
            formData.append(`image_descriptions[${index}]`, '')
          } else {
            console.error('Invalid file object:', fileItem)
          }
        })

        // 调试信息
        console.log('上传文件数量:', this.uploadFiles.length)
        for (let [key, value] of formData.entries()) {
          console.log('FormData:', key, value)
        }

        const response = await itemService.createItem(formData)
        ElMessage.success('物品创建成功')

        // 跳转到物品详情页
        this.$router.push(`/items/${response.data.id}`)

      } catch (error) {
        console.error('创建物品失败:', error)

        // 更详细的错误处理
        let errorMessage = '创建物品失败'
        if (error.response && error.response.data) {
          if (error.response.data.error) {
            errorMessage = error.response.data.error
          } else if (error.response.data.message) {
            errorMessage = error.response.data.message
          } else if (typeof error.response.data === 'string') {
            errorMessage = error.response.data
          }
        } else if (error.message) {
          errorMessage = error.message
        }

        ElMessage.error(errorMessage)
      } finally {
        this.submitting = false
      }
    },

    resetForm() {
      this.$refs.itemFormRef.resetFields()
      this.uploadFiles = []
      this.$refs.uploadRef.clearFiles()
    }
  }
}
</script>

<style scoped>
.item-create {
  padding: 20px;
}

.create-header {
  margin-bottom: 20px;
}

.create-header h2 {
  margin: 10px 0;
  color: #303133;
}

.el-form-item {
  margin-bottom: 22px;
}

:deep(.el-upload--picture-card) {
  width: 120px;
  height: 120px;
}

:deep(.el-upload-list--picture-card .el-upload-list__item) {
  width: 120px;
  height: 120px;
}
</style>
