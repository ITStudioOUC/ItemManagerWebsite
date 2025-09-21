<template>
  <AppHeader />
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
          <div>
            <el-button @click="showImageUpload = true" style="margin-right: 10px;">
              <el-icon><Picture /></el-icon>
              上传图片
            </el-button>
            <el-button type="primary" @click="editMode = !editMode">
              {{ editMode ? '取消编辑' : '编辑' }}
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="item">
        <!-- 物品图片展示 -->
        <el-card class="image-section" style="margin-bottom: 20px;">
          <template #header>
            <span>物品图片</span>
          </template>
          <div v-if="item.images && item.images.length > 0" class="image-gallery">
            <div v-for="image in item.images" :key="image.id" class="image-item">
              <div class="image-container">
                <el-image
                  :src="image.image_url"
                  :preview-src-list="imagePreviewList"
                  fit="cover"
                  class="item-image"
                />
                <!-- 图片操作按钮 -->
                <div class="image-actions">
                  <el-button
                    v-if="!image.is_primary"
                    size="small"
                    type="primary"
                    @click="setPrimaryImage(image.id)"
                    class="action-btn"
                  >
                    设为主图
                  </el-button>
                  <el-button
                    size="small"
                    type="danger"
                    @click="deleteImage(image.id)"
                    class="action-btn"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
              <div class="image-info">
                <el-tag v-if="image.is_primary" type="success" size="small">主图</el-tag>
                <p v-if="image.description" class="image-desc">{{ image.description }}</p>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无图片" />
        </el-card>

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
                  <el-option label="丢失" value="lost" />
                  <el-option label="已弃用" value="abandoned" />
                  <el-option label="禁止借用" value="prohibited" />
                </el-select>
              </el-form-item>
              <el-form-item label="位置">
                <el-input v-model="editableItem.location" />
              </el-form-item>
              <el-form-item label="所有者">
                <el-input v-model="editableItem.owner" :disabled="!editMode" placeholder="请输入所有者姓名" />
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
            <el-descriptions-item label="使用者姓名">{{ item.current_user.username }}</el-descriptions-item>
            <el-descriptions-item label="联系方式">{{ item.current_user.contact }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 使用历史 -->
        <el-card style="margin-top: 20px;">
          <template #header>
            <span>使用历史</span>
          </template>
          <el-table :data="item.usage_history" style="width: 100%">
            <el-table-column prop="user" label="使用者" />
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
            <el-table-column label="图片" width="100">
              <template #default="scope">
                <el-button
                  v-if="scope.row.borrow_images?.length > 0 || scope.row.return_images?.length > 0"
                  size="small"
                  @click="showUsageImages(scope.row)"
                >
                  <el-icon><Picture /></el-icon>
                </el-button>
                <span v-else>-</span>
              </template>
            </el-table-column>
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

    <!-- 物品图片上传对话框 -->
    <el-dialog v-model="showImageUpload" title="上传物品图片" width="500px">
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
          支持 JPG、PNG 格式，最多上传 10 张图片
        </el-text>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showImageUpload = false">取消</el-button>
          <el-button type="primary" @click="uploadImages" :loading="uploading">
            上传
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 使用记录详情对话框 -->
    <el-dialog v-model="showUsageDialog" title="使用记录详情" width="800px">
      <div v-if="selectedUsage">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="使用者">{{ selectedUsage.user }}</el-descriptions-item>
          <el-descriptions-item label="联系方式">{{ selectedUsage.borrower_contact }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDate(selectedUsage.start_time) }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ selectedUsage.end_time ? formatDate(selectedUsage.end_time) : '使用中' }}
          </el-descriptions-item>
          <el-descriptions-item label="使用前状况">{{ selectedUsage.condition_before || '无' }}</el-descriptions-item>
          <el-descriptions-item label="使用后状况">{{ selectedUsage.condition_after || '无' }}</el-descriptions-item>
          <el-descriptions-item label="使用目的">{{ selectedUsage.purpose || '无' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ selectedUsage.notes || '无' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 使用记录图片对话框 -->
    <el-dialog v-model="showUsageImagesDialog" title="使用记录图片" width="800px">
      <div v-if="selectedUsageImages">
        <div v-if="selectedUsageImages.borrow_images?.length > 0" class="usage-images-section">
          <h4>借用时图片</h4>
          <div class="image-gallery">
            <el-image
              v-for="image in selectedUsageImages.borrow_images"
              :key="image.id"
              :src="image.image_url"
              :preview-src-list="borrowImagePreviewList"
              fit="cover"
              class="usage-image"
            />
          </div>
        </div>

        <div v-if="selectedUsageImages.return_images?.length > 0" class="usage-images-section">
          <h4>归还时图片</h4>
          <div class="image-gallery">
            <el-image
              v-for="image in selectedUsageImages.return_images"
              :key="image.id"
              :src="image.image_url"
              :preview-src-list="returnImagePreviewList"
              fit="cover"
              class="usage-image"
            />
          </div>
        </div>

        <div v-if="(!selectedUsageImages.borrow_images || selectedUsageImages.borrow_images.length === 0) &&
                   (!selectedUsageImages.return_images || selectedUsageImages.return_images.length === 0)">
          <el-empty description="暂无图片" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {itemService} from '@/services/api'
import {ElMessage} from 'element-plus'
import AppHeader from '../components/AppHeader.vue'
import { Picture, Plus, ArrowLeft, Delete } from '@element-plus/icons-vue'
import moment from 'moment'

export default {
  name: 'ItemDetail',
  components: {
    AppHeader,
    Picture,
    Plus,
    ArrowLeft,
    Delete
  },
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
      selectedUsage: null,
      showImageUpload: false,
      uploading: false,
      uploadFiles: [],
      showUsageImagesDialog: false,
      selectedUsageImages: null
    }
  },
  computed: {
    imagePreviewList() {
      return this.item?.images?.map(img => img.image_url) || []
    },
    borrowImagePreviewList() {
      return this.selectedUsageImages?.borrow_images?.map(img => img.image_url) || []
    },
    returnImagePreviewList() {
      return this.selectedUsageImages?.return_images?.map(img => img.image_url) || []
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
    showUsageImages(usage) {
      this.selectedUsageImages = usage
      this.showUsageImagesDialog = true
    },
    handleImageChange(file, fileList) {
      this.uploadFiles = fileList
    },
    handleImageRemove(file, fileList) {
      this.uploadFiles = fileList
    },
    async uploadImages() {
      if (this.uploadFiles.length === 0) {
        ElMessage.warning('请选择要上传的图片')
        return
      }

      this.uploading = true
      try {
        const formData = new FormData()
        this.uploadFiles.forEach((file, index) => {
          formData.append('images', file.raw)
          formData.append(`image_descriptions[${index}]`, '')
        })

        await itemService.uploadItemImages(this.id, formData)
        ElMessage.success('图片上传成功')
        this.showImageUpload = false
        this.uploadFiles = []
        this.$refs.uploadRef.clearFiles()
        await this.loadItem()
      } catch (error) {
        console.error('图片上传失败:', error)
        ElMessage.error('图片上传失败')
      } finally {
        this.uploading = false
      }
    },
    async setPrimaryImage(imageId) {
      try {
        await itemService.setPrimaryImage(this.id, imageId)
        ElMessage.success('主图设置成功')
        await this.loadItem()
      } catch (error) {
        console.error('设置主图失败:', error)
        ElMessage.error('设置主图失败')
      }
    },
    async deleteImage(imageId) {
      this.$confirm('确定删除这张图片吗？', '确认删除', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(async () => {
          try {
            await itemService.deleteItemImage(this.id, imageId)
            ElMessage.success('图片删除成功')
            await this.loadItem()
          } catch (error) {
            console.error('删除图片失败:', error)
            ElMessage.error('删除图片失败')
          }
        })
        .catch(() => {
          // 取消删除
        })
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

.image-section {
  margin-bottom: 20px;
}

.image-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  padding: 10px 0;
}

.image-item {
  text-align: center;
}

.item-image {
  width: 200px;
  height: 150px;
  border-radius: 8px;
  cursor: pointer;
}

.usage-image {
  width: 150px;
  height: 120px;
  border-radius: 8px;
  margin: 5px;
  cursor: pointer;
}

.image-info {
  margin-top: 8px;
}

.image-desc {
  font-size: 12px;
  color: #666;
  margin: 4px 0 0 0;
}

.usage-images-section {
  margin-bottom: 20px;
}

.usage-images-section h4 {
  margin-bottom: 10px;
  color: #409eff;
}

.image-container {
  position: relative;
}

.image-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 5px;
}

.action-btn {
  padding: 0 5px;
  font-size: 12px;
}
</style>
