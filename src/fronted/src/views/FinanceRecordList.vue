<template>
  <div>
    <AppHeader />
    <div>
      <el-card>
        <template #header>
          <div class="card-header">
            <span>财务记录</span>
            <el-button type="primary" @click="showAddDialog">添加记录</el-button>
          </div>
        </template>

        <!-- 搜索和筛选区域 -->
        <div class="filter-section">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索标题或描述"
                clearable
                @input="handleSearch">
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-col>
            <el-col :span="4">
              <el-select v-model="typeFilter" placeholder="类型筛选" clearable @change="handleFilter">
                <el-option label="全部" value="" />
                <el-option label="收入" value="income" />
                <el-option label="支出" value="expense" />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-select v-model="departmentFilter" placeholder="部门筛选" clearable @change="handleFilter">
                <el-option label="全部部门" value="" />
                <el-option
                  v-for="dept in departments"
                  :key="dept.id"
                  :label="dept.name"
                  :value="dept.id" />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-select v-model="categoryFilter" placeholder="类别筛选" clearable @change="handleFilter">
                <el-option label="全部类别" value="" />
                <el-option
                  v-for="cat in categories"
                  :key="cat.id"
                  :label="cat.name"
                  :value="cat.id" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                @change="handleFilter">
              </el-date-picker>
            </el-col>
          </el-row>
        </div>

        <el-table :data="paginatedRecords" style="width: 100%" v-loading="loading">
          <el-table-column prop="title" label="标题" min-width="150"></el-table-column>
          <el-table-column prop="amount" label="金额" width="120" sortable>
            <template #default="scope">
              <span :class="['amount', scope.row.record_type]">
                {{ scope.row.record_type === 'income' ? '+' : '-' }}¥{{ scope.row.amount }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="record_type" label="类型" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.record_type === 'income' ? 'success' : 'danger'">
                {{ scope.row.record_type === 'income' ? '收入' : '支出' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="transaction_date" label="交易日期" width="120" sortable></el-table-column>
          <el-table-column prop="department" label="部门" width="120">
            <template #default="scope">
              {{ scope.row.department ? scope.row.department.name : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="category" label="类别" width="120">
            <template #default="scope">
              {{ scope.row.category ? scope.row.category.name : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="fund_manager" label="批准人" width="120">
            <template #default="scope">
              {{ scope.row.fund_manager || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="250" fixed="right">
            <template #default="scope">
              <el-button size="small" @click="showDetail(scope.row.id)">详情</el-button>
              <el-button size="small" @click="showEditDialog(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteRecord(scope.row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页组件 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="filteredRecords.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange">
          </el-pagination>
        </div>
      </el-card>

      <el-dialog :title="dialogTitle" v-model="dialogVisible" width="70%">
        <finance-record-form
            :record="selectedRecord"
            @submit="handleFormSubmit"
            @cancel="dialogVisible = false"
        ></finance-record-form>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import { financeService } from '@/services/api';
import FinanceRecordForm from './FinanceRecordForm.vue';
import AppHeader from "@/components/AppHeader.vue";
import { Search } from '@element-plus/icons-vue';

export default {
  name: 'FinanceRecordList',
  components: {
    AppHeader,
    FinanceRecordForm,
    Search,
  },
  data() {
    return {
      records: [],
      departments: [],
      categories: [],
      dialogVisible: false,
      dialogTitle: '',
      selectedRecord: null,
      loading: false,
      // 搜索和筛选
      searchKeyword: '',
      typeFilter: '',
      departmentFilter: '',
      categoryFilter: '',
      dateRange: null,
      // 分页
      currentPage: 1,
      pageSize: 20,
    };
  },
  computed: {
    filteredRecords() {
      let filtered = [...this.records];

      // 搜索过滤
      if (this.searchKeyword) {
        const keyword = this.searchKeyword.toLowerCase();
        filtered = filtered.filter(record =>
          record.title.toLowerCase().includes(keyword) ||
          (record.description && record.description.toLowerCase().includes(keyword)) ||
          (record.fund_manager && record.fund_manager.toLowerCase().includes(keyword)) ||
          (record.fund_receiver && record.fund_receiver.toLowerCase().includes(keyword))
        );
      }

      // 类型筛选
      if (this.typeFilter) {
        filtered = filtered.filter(record => record.record_type === this.typeFilter);
      }

      // 部门筛选
      if (this.departmentFilter) {
        filtered = filtered.filter(record =>
          record.department && record.department.id === this.departmentFilter
        );
      }

      // 类别筛选
      if (this.categoryFilter) {
        filtered = filtered.filter(record =>
          record.category && record.category.id === this.categoryFilter
        );
      }

      // 日期范围筛选
      if (this.dateRange && this.dateRange.length === 2) {
        const [startDate, endDate] = this.dateRange;
        filtered = filtered.filter(record => {
          const recordDate = record.transaction_date;
          return recordDate >= startDate && recordDate <= endDate;
        });
      }

      return filtered;
    },
    paginatedRecords() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.filteredRecords.slice(start, end);
    }
  },
  async created() {
    await this.loadData();
  },
  methods: {
    async loadData() {
      await Promise.all([
        this.fetchRecords(),
        this.fetchDepartments(),
        this.fetchCategories()
      ]);
    },
    async fetchRecords() {
      this.loading = true;
      try {
        const response = await financeService.getAllFinanceRecords();
        this.records = response.data;
      } catch (error) {
        this.$message.error('获取财务记录失败');
      } finally {
        this.loading = false;
      }
    },
    async fetchDepartments() {
      try {
        const response = await financeService.getAllDepartments();
        this.departments = response.data;
      } catch (error) {
        console.error('获取部门列表失败:', error);
      }
    },
    async fetchCategories() {
      try {
        const response = await financeService.getAllCategories();
        this.categories = response.data;
      } catch (error) {
        console.error('获取类别列表失败:', error);
      }
    },
    handleSearch() {
      this.currentPage = 1; // 搜索时重置到第一页
    },
    handleFilter() {
      this.currentPage = 1; // 筛选时重置到第一页
    },
    handleSizeChange(size) {
      this.pageSize = size;
      this.currentPage = 1;
    },
    handleCurrentChange(page) {
      this.currentPage = page;
    },
    showAddDialog() {
      this.selectedRecord = null;
      this.dialogTitle = '添加财务记录';
      this.dialogVisible = true;
    },
    showEditDialog(record) {
      this.selectedRecord = { ...record };
      this.dialogTitle = '编辑财务记录';
      this.dialogVisible = true;
    },
    showDetail(recordId) {
      this.$router.push(`/finance/records/${recordId}`);
    },
    async deleteRecord(id) {
      try {
        await this.$confirm('确认删除这条财务记录？', '确认删除', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        });

        await financeService.deleteFinanceRecord(id);
        this.fetchRecords();
        this.$message.success('删除成功');
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('删除失败');
        }
      }
    },
    handleFormSubmit() {
      this.dialogVisible = false;
      this.fetchRecords();
    },
  },
};
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.amount.income {
  color: #67c23a;
  font-weight: bold;
}

.amount.expense {
  color: #f56c6c;
  font-weight: bold;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
