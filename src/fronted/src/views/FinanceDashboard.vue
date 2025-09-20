<template>
  <div>
    <AppHeader />
    <div class="finance-dashboard">
      <!-- 总体统计 -->
      <el-card class="summary-card">
        <template #header>
          <span>财务概览</span>
        </template>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="总收入" :value="totalIncome" :precision="2" suffix="元">
              <template #prefix>
                <el-icon style="vertical-align: middle;"><TrendCharts /></el-icon>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="总支出" :value="totalExpense" :precision="2" suffix="元">
              <template #prefix>
                <el-icon style="vertical-align: middle;"><Money /></el-icon>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="总剩余资金" :value="netProfit" :precision="2" suffix="元"
                         :value-style="netProfit >= 0 ? 'color: #67c23a' : 'color: #f56c6c'">
              <template #prefix>
                <el-icon style="vertical-align: middle;"><Wallet /></el-icon>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="记录总数" :value="totalRecords">
              <template #prefix>
                <el-icon style="vertical-align: middle;"><Document /></el-icon>
              </template>
            </el-statistic>
          </el-col>
        </el-row>
      </el-card>

      <!-- 本月统计 -->
      <el-card class="monthly-card">
        <template #header>
          <span>{{ currentMonth }}月统计</span>
        </template>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-statistic title="本月收入" :value="monthlyIncome" :precision="2" suffix="元"
                         value-style="color: #67c23a">
            </el-statistic>
          </el-col>
          <el-col :span="8">
            <el-statistic title="本月支出" :value="monthlyExpense" :precision="2" suffix="元"
                         value-style="color: #f56c6c">
            </el-statistic>
          </el-col>
          <el-col :span="8">
            <el-statistic title="流水总结" :value="monthlyNet" :precision="2" suffix="元"
                         :value-style="monthlyNet >= 0 ? 'color: #67c23a' : 'color: #f56c6c'">
            </el-statistic>
          </el-col>
        </el-row>
      </el-card>

      <!-- 部门财务统计 -->
      <el-card class="department-card">
        <template #header>
          <span>重点部门财务统计</span>
        </template>
        <el-row :gutter="20">
          <el-col :span="8" v-for="dept in keyDepartments" :key="dept.name">
            <el-card class="dept-stat-card" :class="dept.name">
              <h3>{{ dept.name }}</h3>
              <div class="dept-stats">
                <div class="stat-item">
                  <span class="label">收入:</span>
                  <span class="value income">+¥{{ dept.income.toFixed(2) }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">支出:</span>
                  <span class="value expense">-¥{{ dept.expense.toFixed(2) }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">余额:</span>
                  <span class="value" :class="dept.balance >= 0 ? 'positive' : 'negative'">
                    ¥{{ dept.balance.toFixed(2) }}
                  </span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-card>

      <!-- 收支流水图 -->
      <el-card class="chart-card">
        <template #header>
          <span>收支流水图</span>
        </template>
        <div ref="chart" style="height: 400px;"></div>
      </el-card>
    </div>
  </div>
</template>

<script>
import {financeService} from '@/services/api';
import * as echarts from 'echarts';
import {Document, Money, TrendCharts, Wallet} from '@element-plus/icons-vue';
import AppHeader from '@/components/AppHeader.vue';

export default {
  name: 'FinanceDashboard',
  components: {
    AppHeader,
    TrendCharts,
    Money,
    Wallet,
    Document
  },
  data() {
    return {
      records: [],
      chart: null,
      currentMonth: new Date().getMonth() + 1,
      keyDepartmentNames: ['爱特工作室本部', 'UI部', '游戏部']
    };
  },
  computed: {
    totalIncome() {
      return this.records
        .filter(r => r.record_type === 'income')
        .reduce((sum, r) => sum + parseFloat(r.amount), 0);
    },
    totalExpense() {
      return this.records
        .filter(r => r.record_type === 'expense')
        .reduce((sum, r) => sum + parseFloat(r.amount), 0);
    },
    netProfit() {
      return this.totalIncome - this.totalExpense;
    },
    totalRecords() {
      return this.records.length;
    },
    monthlyIncome() {
      const currentMonth = new Date().getMonth() + 1;
      const currentYear = new Date().getFullYear();
      return this.records
        .filter(r => {
          const recordDate = new Date(r.transaction_date);
          return r.record_type === 'income' &&
                 recordDate.getMonth() + 1 === currentMonth &&
                 recordDate.getFullYear() === currentYear;
        })
        .reduce((sum, r) => sum + parseFloat(r.amount), 0);
    },
    monthlyExpense() {
      const currentMonth = new Date().getMonth() + 1;
      const currentYear = new Date().getFullYear();
      return this.records
        .filter(r => {
          const recordDate = new Date(r.transaction_date);
          return r.record_type === 'expense' &&
                 recordDate.getMonth() + 1 === currentMonth &&
                 recordDate.getFullYear() === currentYear;
        })
        .reduce((sum, r) => sum + parseFloat(r.amount), 0);
    },
    monthlyNet() {
      return this.monthlyIncome - this.monthlyExpense;
    },
    keyDepartments() {
      return this.keyDepartmentNames.map(deptName => {
        const deptRecords = this.records.filter(r =>
          r.department && r.department.name === deptName
        );

        const income = deptRecords
          .filter(r => r.record_type === 'income')
          .reduce((sum, r) => sum + parseFloat(r.amount), 0);

        const expense = deptRecords
          .filter(r => r.record_type === 'expense')
          .reduce((sum, r) => sum + parseFloat(r.amount), 0);

        return {
          name: deptName,
          income,
          expense,
          balance: income - expense
        };
      });
    }
  },
  async created() {
    await this.fetchRecords();
    this.$nextTick(() => {
      this.initChart();
    });
  },
  methods: {
    async fetchRecords() {
      try {
        const response = await financeService.getAllFinanceRecords();
        this.records = response.data;
      } catch (error) {
        this.$message.error('获取财务记录失败');
      }
    },
    initChart() {
      if (!this.$refs.chart) return;

      this.chart = echarts.init(this.$refs.chart);
      const dates = [...new Set(this.records.map(r => r.transaction_date))].sort();

      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            let result = params[0].axisValueLabel + '<br/>';
            params.forEach(param => {
              result += `${param.seriesName}: ¥${param.value}<br/>`;
            });
            return result;
          }
        },
        legend: {
          data: ['收入', '支出']
        },
        xAxis: {
          type: 'category',
          data: dates,
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: '¥{value}'
          }
        },
        series: [
          {
            name: '收入',
            type: 'line',
            smooth: true,
            itemStyle: { color: '#67c23a' },
            data: this.getChartData('income', dates),
            label: {
              show: false,
              position: 'top',
              formatter: '¥{c}',
              color: '#67c23a',
              fontWeight: 'bold'
            },
            emphasis: {
              label: {
                show: true
              }
            }
          },
          {
            name: '支出',
            type: 'line',
            smooth: true,
            itemStyle: { color: '#f56c6c' },
            data: this.getChartData('expense', dates),
            label: {
              show: false,
              position: 'top',
              formatter: '¥{c}',
              color: '#f56c6c',
              fontWeight: 'bold'
            },
            emphasis: {
              label: {
                show: true
              }
            }
          },
        ],
      };
      this.chart.setOption(option);

      // 添加点击事件监听器
      this.chart.on('click', (params) => {
        const { seriesName, value, name: date, dataIndex } = params;

        // 获取该日期的详细记录
        const dayRecords = this.records.filter(r => r.transaction_date === date);
        const typeRecords = dayRecords.filter(r =>
          (seriesName === '收入' && r.record_type === 'income') ||
          (seriesName === '支出' && r.record_type === 'expense')
        );

        // 构建详细信息
        let detailInfo = `<div>
          <h3 style="margin: 0 0 15px 0; color: #409eff;">${date} - ${seriesName}</h3>
          <p style="margin: 0 0 10px 0; font-size: 18px; font-weight: bold; color: ${seriesName === '收入' ? '#67c23a' : '#f56c6c'};">
            总计: ¥${value.toFixed(2)}
          </p>
          <div style="max-height: 300px; overflow-y: auto;">`;

        if (typeRecords.length > 0) {
          detailInfo += `<p style="margin: 0 0 10px 0; font-weight: bold;">具体记录 (${typeRecords.length}条):</p>`;
          typeRecords.forEach((record, index) => {
            detailInfo += `
              <div style="padding: 8px; margin-bottom: 8px; background-color: #f5f7fa; border-radius: 4px; border-left: 3px solid ${seriesName === '收入' ? '#67c23a' : '#f56c6c'};">
                <div style="font-weight: bold; color: #303133;">${record.title}</div>
                <div style="display: flex; justify-content: space-between; margin-top: 4px;">
                  <span style="color: #606266;">¥${parseFloat(record.amount).toFixed(2)}</span>
                  ${record.department ? `<span style="color: #909399; font-size: 12px;">${record.department.name}</span>` : ''}
                </div>
                ${record.description ? `<div style="color: #909399; font-size: 12px; margin-top: 4px;">${record.description}</div>` : ''}
              </div>`;
          });
        } else {
          detailInfo += '<p style="color: #909399;">该日期无相关记录</p>';
        }

        detailInfo += '</div></div>';

        // 显示详细信息对话框
        this.$alert(detailInfo, '财务详情', {
          dangerouslyUseHTMLString: true,
          customClass: 'finance-detail-alert',
          showClose: true,
          closeOnClickModal: true,
          closeOnPressEscape: true
        }).catch(() => { /* 关闭时不做操作，否则会炸 */ });
      });

      // 添加鼠标悬停时显示数据标签
      this.chart.on('mouseover', (params) => {
        const option = this.chart.getOption();
        option.series[params.seriesIndex].label.show = true;
        this.chart.setOption(option);
      });

      this.chart.on('mouseout', (params) => {
        const option = this.chart.getOption();
        option.series[params.seriesIndex].label.show = false;
        this.chart.setOption(option);
      });
    },
    getChartData(type, dates) {
      const data = {};
      this.records
        .filter(r => r.record_type === type)
        .forEach(r => {
          if (data[r.transaction_date]) {
            data[r.transaction_date] += parseFloat(r.amount);
          } else {
            data[r.transaction_date] = parseFloat(r.amount);
          }
        });

      return dates.map(date => data[date] || 0);
    },
  },
};
</script>

<style scoped>
.finance-dashboard {
  padding: 20px;
}

.summary-card, .monthly-card, .department-card, .chart-card {
  margin-bottom: 20px;
}

.dept-stat-card {
  height: 180px;
  text-align: center;
  transition: transform 0.3s, box-shadow 0.3s;
}

.dept-stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.dept-stat-card h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #409eff;
}

.dept-stats {
  text-align: left;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding: 5px 0;
}

.stat-item .label {
  font-weight: bold;
  color: #666;
}

.stat-item .value {
  font-weight: bold;
  font-size: 16px;
}

.value.income {
  color: #67c23a;
}

.value.expense {
  color: #f56c6c;
}

.value.positive {
  color: #67c23a;
}

.value.negative {
  color: #f56c6c;
}

/* 部门特色样式 */
.dept-stat-card.爱特工作室本部 {
  border-left: 4px solid #409eff;
}

.dept-stat-card.UI部 {
  border-left: 4px solid #67c23a;
}

.dept-stat-card.游戏部 {
  border-left: 4px solid #e6a23c;
}
</style>
