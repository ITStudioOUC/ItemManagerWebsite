<template>
  <el-form :model="form" ref="form" label-width="100px">
    <el-form-item label="标题" prop="title" required>
      <el-input v-model="form.title"></el-input>
    </el-form-item>
    <el-form-item label="金额" prop="amount" required>
      <el-input-number v-model="form.amount" :precision="2" :step="1"></el-input-number>
    </el-form-item>
    <el-form-item label="记录类型" prop="record_type" required>
      <el-radio-group v-model="form.record_type">
        <el-radio label="expense">支出</el-radio>
        <el-radio label="income">收入</el-radio>
      </el-radio-group>
    </el-form-item>
    <el-form-item label="日期" prop="transaction_date" required>
      <el-date-picker v-model="form.transaction_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD"></el-date-picker>
    </el-form-item>
    <el-form-item label="所属部门" prop="department">
      <el-select v-model="form.department" placeholder="请选择部门">
        <el-option v-for="dept in departments" :key="dept.id" :label="dept.name" :value="dept.id"></el-option>
      </el-select>
    </el-form-item>
    <el-form-item label="类别" prop="category">
      <el-select v-model="form.category" placeholder="请选择类别">
        <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id"></el-option>
      </el-select>
    </el-form-item>
    <el-form-item label="描述" prop="description">
      <el-input v-model="form.description" type="textarea" rows="3" placeholder="必须注明所有信息"></el-input>
    </el-form-item>

    <!-- 批准人字段 -->
    <el-form-item label="批准人" prop="fund_manager">
      <el-input v-model="form.fund_manager" placeholder="批准这条账目的人"></el-input>
    </el-form-item>

    <!-- 凭证图片上传区域 -->
    <el-form-item label="凭证图片" v-if="record">
      <div class="image-upload-section">
        <el-upload
          :action="uploadAction"
          :http-request="handleUpload"
          :show-file-list="false"
          list-type="picture-card"
          accept="image/*"
          multiple>
          <div class="upload-placeholder">
            <el-icon><Plus /></el-icon>
            <div class="upload-text">添加凭证</div>
          </div>
        </el-upload>

        <!-- 已有图片展示 -->
        <div class="existing-images" v-if="existingImages.length > 0">
          <div
            v-for="image in existingImages"
            :key="image.id"
            class="existing-image-item">
            <div class="image-container">
              <img
                :src="getImageUrl(image.image)"
                :alt="image.description || '凭证图片'"
                @click="showImagePreview(image)"
                class="proof-image">
              <div class="image-overlay">
                <el-button
                  type="danger"
                  size="small"
                  circle
                  @click="deleteExistingImage(image.id)"
                  class="delete-btn">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 新上传图片展示 -->
        <div class="new-images" v-if="newImages.length > 0">
          <div
            v-for="(image, index) in newImages"
            :key="'new-' + index"
            class="new-image-item">
            <div class="image-container">
              <img
                :src="image.url"
                :alt="'新上传图片'"
                class="proof-image">
              <div class="image-overlay">
                <el-button
                  type="danger"
                  size="small"
                  circle
                  @click="removeNewImage(index)"
                  class="delete-btn">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-form-item>

    <el-form-item>
      <el-button type="primary" @click="submitForm">提交</el-button>
      <el-button @click="cancel">取消</el-button>
    </el-form-item>
  </el-form>

  <!-- 图片预览对话框 -->
  <el-dialog v-model="previewVisible" title="图片预览" width="60%">
    <div class="image-preview-container">
      <img :src="previewImageUrl" alt="预览图片" class="preview-image">
    </div>
  </el-dialog>
</template>

<script>
import { financeService, API_BASE_URL_WITHOUT_API } from '@/services/api';
import { Plus, Delete } from '@element-plus/icons-vue';

export default {
  name: 'FinanceRecordForm',
  components: {
    Plus,
    Delete
  },
  props: {
    record: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      form: {
        title: '',
        amount: 0,
        record_type: 'expense',
        transaction_date: '',
        department: null,
        category: null,
        description: '',
        fund_manager: '',
      },
      departments: [],
      categories: [],
      existingImages: [], // 已有的图片
      newImages: [], // 新上传的图片
      previewVisible: false,
      previewImageUrl: '',
      uploadAction: ''
    };
  },
  watch: {
    record: {
      handler(newVal) {
        if (newVal) {
          // 处理编辑时的数据填充
          this.form = {
            title: newVal.title || '',
            amount: newVal.amount || 0,
            record_type: newVal.record_type || 'expense',
            transaction_date: newVal.transaction_date || '',
            department: newVal.department ? newVal.department.id : null,
            category: newVal.category ? newVal.category.id : null,
            description: newVal.description || '',
            fund_manager: newVal.fund_manager || '',
          };
          this.existingImages = newVal.proof_images || [];
          this.newImages = [];
        } else {
          this.resetForm();
        }
      },
      immediate: true,
    },
  },
  async created() {
    this.fetchDepartments();
    this.fetchCategories();
  },
  methods: {
    async fetchDepartments() {
      try {
        const response = await financeService.getAllDepartments();
        this.departments = response.data;
      } catch (error) {
        this.$message.error('获取部门列表失败');
      }
    },
    async fetchCategories() {
      try {
        const response = await financeService.getAllCategories();
        this.categories = response.data;
      } catch (error) {
        this.$message.error('获取类别列表失败');
      }
    },
    async submitForm() {
      this.$refs.form.validate(async (valid) => {
        if (valid) {
          try {
            let recordId;

            // 首先提交基本表单数据
            const formData = new FormData();
            Object.keys(this.form).forEach(key => {
              const value = this.form[key];
              if (value !== null && value !== undefined && value !== '') {
                formData.append(key, value);
              }
            });

            if (this.record) {
              // 更新记录 - 只更新基本信息，不处理图片
              await financeService.updateFinanceRecord(this.record.id, formData);
              recordId = this.record.id;
              this.$message.success('记录更新成功');

              // 如果有新图片，单独上传（只在编辑模式下且有新图片时）
              if (this.newImages.length > 0) {
                const imageFormData = new FormData();
                this.newImages.forEach((image) => {
                  imageFormData.append('images', image.file);
                });

                await financeService.uploadImages(recordId, imageFormData);
                this.$message.success('新增凭证图片上传成功');
              }
            } else {
              // 创建新记录
              const response = await financeService.createFinanceRecord(formData);
              recordId = response.data.id;
              this.$message.success('记录创建成功');

              // 如果有新图片，单独上传
              if (this.newImages.length > 0) {
                const imageFormData = new FormData();
                this.newImages.forEach((image) => {
                  imageFormData.append('images', image.file);
                });

                await financeService.uploadImages(recordId, imageFormData);
                this.$message.success('凭证图片上传成功');
              }
            }

            this.$emit('submit');
          } catch (error) {
            console.error('提交失败:', error);
            this.$message.error('操作失败: ' + (error.response?.data?.detail || '未知错误，请查看控制台'));
          }
        }
      });
    },
    cancel() {
      this.$emit('cancel');
    },
    resetForm() {
      this.form = {
        title: '',
        amount: 0,
        record_type: 'expense',
        transaction_date: '',
        department: null,
        category: null,
        description: '',
        fund_manager: '',
      };
      this.existingImages = [];
      this.newImages = [];
    },
    handleUpload(options) {
      // 简化上传逻辑，直接保存文件对象，在提交表单时一起上传
      const file = options.file;

      // 创建预览URL
      const previewUrl = URL.createObjectURL(file);

      // 添加到新图片列表
      this.newImages.push({
        file: file,
        url: previewUrl,
        name: file.name
      });

      // 调用成功回调
      if (options.onSuccess) {
        options.onSuccess();
      }
    },
    showImagePreview(image) {
      if (image.image) {
        // 已有图片
        this.previewImageUrl = this.getImageUrl(image.image);
      } else {
        // 新上传图片
        this.previewImageUrl = image.url;
      }
      this.previewVisible = true;
    },
    getImageUrl(imagePath) {
      if (!imagePath) return '';
      return imagePath.startsWith('http')
        ? imagePath
        : `${API_BASE_URL_WITHOUT_API}${imagePath}`;
    },
    async deleteExistingImage(imageId) {
      try {
        await this.$confirm('确定删除这张图片吗？', '确认删除', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        });

        await financeService.deleteProofImage(imageId);
        this.$message.success('删除成功');
        this.existingImages = this.existingImages.filter(img => img.id !== imageId);
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('删除失败');
        }
      }
    },
    removeNewImage(index) {
      this.newImages.splice(index, 1);
    },
  },
};
</script>

<style scoped>
.image-upload-section {
  position: relative;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100px;
  border: 2px dashed #d3d3d3;
  border-radius: 4px;
  cursor: pointer;
}

.upload-placeholder:hover {
  border-color: #409eff;
}

.upload-placeholder .el-icon {
  font-size: 28px;
  color: #409eff;
}

.upload-placeholder .upload-text {
  margin-top: 8px;
  font-size: 14px;
  color: #666;
}

.existing-images,
.new-images {
  display: flex;
  flex-wrap: wrap;
  margin-top: 10px;
}

.existing-image-item,
.new-image-item {
  position: relative;
  margin-right: 10px;
  margin-bottom: 10px;
}

.image-container {
  position: relative;
}

.proof-image {
  display: block;
  max-width: 100px;
  max-height: 100px;
  object-fit: cover;
  border-radius: 4px;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.existing-image-item:hover .image-overlay,
.new-image-item:hover .image-overlay {
  opacity: 1;
}

.delete-btn {
  background-color: rgba(255, 255, 255, 0.8);
  border: none;
  cursor: pointer;
}

.delete-btn:hover {
  background-color: rgba(255, 255, 255, 1);
}

.image-preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
</style>
