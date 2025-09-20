<template>
  <div>
    <AppHeader />
    <div class="finance-detail-container">
      <div class="detail-header">
        <el-button @click="$router.go(-1)" style="margin-bottom: 20px;">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
      </div>
      <el-card v-if="record">
        <template #header>
          <div class="card-header">
            <span>财务记录详情</span>
            <div>
              <el-button @click="showEditDialog" type="primary">编辑</el-button>
            </div>
          </div>
        </template>

        <div class="record-details">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="detail-item">
                <label>标题：</label>
                <span>{{ record.title }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="detail-item">
                <label>金额：</label>
                <span class="amount" :class="record.record_type">
                  {{ record.record_type === 'income' ? '+' : '-' }}¥{{ record.amount }}
                </span>
              </div>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <div class="detail-item">
                <label>类型：</label>
                <el-tag :type="record.record_type === 'income' ? 'success' : 'danger'">
                  {{ record.record_type === 'income' ? '收入' : '支出' }}
                </el-tag>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="detail-item">
                <label>交易日期：</label>
                <span>{{ record.transaction_date }}</span>
              </div>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <div class="detail-item">
                <label>所属部门：</label>
                <span>{{ record.department ? record.department.name : '-' }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="detail-item">
                <label>类别：</label>
                <span>{{ record.category ? record.category.name : '-' }}</span>
              </div>
            </el-col>
          </el-row>

          <el-row v-if="record.description">
            <el-col :span="24">
              <div class="detail-item">
                <label>描述：</label>
                <p class="description">{{ record.description }}</p>
              </div>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <div class="detail-item">
                <label>批准人：</label>
                <span>{{ record.fund_manager || '-' }}</span>
              </div>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="24">
              <div class="detail-item">
                <label>创建时间：</label>
                <span>{{ formatDateTime(record.created_at) }}</span>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 凭证图片区域 -->
        <el-divider>交易凭证</el-divider>
        <div class="proof-images-section">
          <div class="images-grid" v-if="record.proof_images && record.proof_images.length > 0">
            <div
              v-for="image in record.proof_images"
              :key="image.id"
              class="image-item">
              <div class="image-container">
                <img
                  :src="getImageUrl(image.image)"
                  :alt="image.description || '凭证图片'"
                  @click="showImagePreview(image)"
                  class="proof-image">
              </div>
              <p class="image-description" v-if="image.description">{{ image.description }}</p>
            </div>
          </div>

          <div v-else class="no-images">
            <p>暂无凭证图片</p>
            <p class="tip">可通过编辑记录来添加凭证图片</p>
          </div>
        </div>
      </el-card>

      <!-- 图片预览对话框 -->
      <el-dialog v-model="previewVisible" title="凭证图片" width="60%">
        <div class="image-preview-container">
          <img :src="previewImageUrl" alt="凭证图片" class="preview-image">
        </div>
      </el-dialog>

      <!-- 编辑对话框 -->
      <el-dialog :title="'编辑财务记录'" v-model="editDialogVisible" width="60%">
        <finance-record-form
          :record="record"
          @submit="handleEditSubmit"
          @cancel="editDialogVisible = false"
        ></finance-record-form>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import {API_BASE_URL_WITHOUT_API, financeService} from '@/services/api';
import {Delete, Plus} from '@element-plus/icons-vue';
import AppHeader from "@/components/AppHeader.vue";
import FinanceRecordForm from './FinanceRecordForm.vue';

export default {
  name: 'FinanceRecordDetail',
  components: {
    AppHeader,
    FinanceRecordForm,
    Plus,
    Delete
  },
  data() {
    return {
      record: null,
      previewVisible: false,
      previewImageUrl: '',
      editDialogVisible: false,
      uploadAction: ''
    };
  },
  async created() {
    await this.fetchRecord();
  },
  methods: {
    async fetchRecord() {
      try {
        const response = await financeService.getFinanceRecord(this.$route.params.id);
        this.record = response.data;
      } catch (error) {
        this.$message.error('获取记录详情失败');
        this.$router.go(-1);
      }
    },

    getImageUrl(imagePath) {
      if (!imagePath) return '';
      return imagePath.startsWith('http')
        ? imagePath
        : `${API_BASE_URL_WITHOUT_API}${imagePath}`;
    },

    showImagePreview(image) {
      this.previewImageUrl = this.getImageUrl(image.image);
      this.previewVisible = true;
    },

    showEditDialog() {
      this.editDialogVisible = true;
    },

    async handleEditSubmit() {
      this.editDialogVisible = false;
      await this.fetchRecord();
    },

    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return '';
      return new Date(dateTimeStr).toLocaleString('zh-CN');
    }
  }
};
</script>

<style scoped>
.finance-detail-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.record-details {
  margin-bottom: 20px;
}

.detail-item {
  margin-bottom: 15px;
}

.detail-item label {
  font-weight: bold;
  margin-right: 8px;
  color: #666;
}

.amount.income {
  color: #67c23a;
  font-weight: bold;
}

.amount.expense {
  color: #f56c6c;
  font-weight: bold;
}

.description {
  margin: 5px 0;
  line-height: 1.6;
  color: #333;
}

.proof-images-section {
  margin-top: 20px;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.image-item {
  text-align: center;
}

.image-container {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.proof-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.3s;
}

.proof-image:hover {
  transform: scale(1.05);
}

.image-description {
  margin-top: 8px;
  font-size: 12px;
  color: #666;
}

.no-images {
  text-align: center;
  color: #999;
  padding: 40px 0;
}

.image-preview-container {
  text-align: center;
}

.preview-image {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
}
</style>
