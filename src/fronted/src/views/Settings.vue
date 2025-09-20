<template>
  <div class="settings-page">
    <AppHeader />
    <div class="settings-container">
      <div class="settings-header">
        <h2>网站设置及说明</h2>
      </div>

      <div class="settings-content">
        <!-- 邮箱通知设置 -->
        <el-card class="setting-card" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><Message /></el-icon>
              <span>通知设置</span>
            </div>
          </template>

          <!-- 全局邮件通知开关 -->
          <div class="setting-item">
            <div class="setting-label">
              <span>邮件通知</span>
              <p class="setting-desc">开启后，所有数据修改操作将发送邮件通知</p>
            </div>
            <div class="setting-control">
              <el-switch
                v-model="emailNotificationEnabled"
                @change="saveEmailNotificationSetting"
                active-text="开启"
                inactive-text="关闭"
                active-color="#67c23a"
                inactive-color="#dcdfe6"
              />
            </div>
          </div>

          <!-- 邮箱管理 -->
          <div class="setting-item" style="flex-direction: column; align-items: flex-start;">
            <div class="setting-label" style="margin-bottom: 15px;">
              <span>通知邮箱管理</span>
              <p class="setting-desc">管理接收通知的邮箱列表，可以单独启用/禁用每个邮箱</p>
            </div>

            <!-- 现有邮箱列表 -->
            <div v-if="allEmails.length > 0" class="email-management-section">
              <h4>现有邮箱</h4>
              <div class="existing-emails">
                <div
                  v-for="emailItem in allEmails"
                  :key="emailItem.id"
                  class="email-management-item"
                >
                  <div class="email-info">
                    <span class="email-address">{{ emailItem.email }}</span>
                    <span v-if="emailItem.description" class="email-description">{{ emailItem.description }}</span>
                  </div>
                  <div class="email-actions">
                    <el-switch
                      :model-value="emailItem.is_enabled"
                      @change="(value) => toggleEmailStatus(emailItem.id, value)"
                      size="small"
                      active-color="#67c23a"
                      inactive-color="#f56c6c"
                    />
                    <el-button
                      type="danger"
                      size="small"
                      @click="removeExistingEmail(emailItem.id)"
                      class="delete-email-btn"
                    >
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 添加新邮箱 -->
            <div class="email-management-section">
              <h4>添加新邮箱</h4>
              <div class="new-email-form">
                <div class="form-row">
                  <el-input
                    v-model="newEmail.email"
                    placeholder="请输入邮箱地址"
                    style="flex: 1; margin-right: 10px;"
                  />
                  <el-input
                    v-model="newEmail.description"
                    placeholder="描述（可选）"
                    style="flex: 1; margin-right: 10px;"
                  />
                  <el-switch
                    v-model="newEmail.is_enabled"
                    active-text="启用"
                    inactive-text="禁用"
                    size="small"
                    style="margin-right: 10px;"
                  />
                  <el-button
                    type="primary"
                    :icon="Plus"
                    @click="addNewEmail"
                  >
                    添加
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 网站说明 -->
        <el-card class="setting-card" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><InfoFilled /></el-icon>
              <span>网站说明</span>
            </div>
          </template>
          <div class="content-section">
            <h3>系统介绍</h3>
            <p>爱特工作室物品管理及财务管理系统是为爱特工作室量身定制的综合管理平台，主要功能包括：</p>
            <ul>
              <li><strong>物品管理：</strong>管理工作室的各类物品，包括电子设备、办公用品等</li>
              <li><strong>借用记录：</strong>跟踪物品的借用情况，确保物品流转透明化</li>
              <li><strong>财务管理：</strong>记录工作室的收支情况，支持多部门资金管理</li>
              <li><strong>数据统计：</strong>提供直观的数据可视化界面</li>
            </ul>

            <h3>使用说明</h3>
            <ol>
              <li>物品管理：可以添加、编辑、删除物品信息，查看物品状态</li>
              <li>借用流程：选择物品 → 填写借用信息 → 确认借用 → 归还确认</li>
              <li>财务记录：添加收支记录，支持上传凭证图片</li>
              <li>权限管理：不同用户具有不同的操作权限</li>
            </ol>

            <h3>免责声明</h3>
            <div class="disclaimer">
              <p><strong>重要提醒：</strong></p>
              <ul>
                <li>本系统仅供爱特工作室内部使用，请勿泄露系统访问信息</li>
                <li>用户需对自己的操作行为负责，误操作造成的数据丢失由操作者承担责任</li>
                <li>系统会记录所有用户操作日志，请规范使用</li>
                <li>如发现系统异常或安全问题，请及时联系管理员</li>
                <li>系统数据会定期备份，但建议重要数据另行保存</li>
              </ul>
            </div>

            <h3>联系方式</h3>
            <p>如有问题或建议，请联系系统管理员：</p>
            <ul>
              <li>邮箱：admin@itstudio.com</li>
              <li>QQ群：123456789</li>
              <li>技术支持：Web部、站长</li>
            </ul>

            <h3>版本信息</h3>
            <p>
              当前版本：v1.0.0<br>
              更新时间：2024年9月<br>
              开发团队：爱特工作室
            </p>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script>
import {onMounted, ref} from 'vue'
import {ElMessage} from 'element-plus'
import {Delete, InfoFilled, Message, Plus} from '@element-plus/icons-vue'
import AppHeader from '@/components/AppHeader.vue'
import {API_BASE_URL_WITHOUT_API} from '@/services/api'

export default {
  name: 'Settings',
  components: {
    AppHeader,
    Message,
    InfoFilled,
    Plus,
    Delete
  },
  setup() {
    const emailNotificationEnabled = ref(false)
    const allEmails = ref([])
    const newEmail = ref({
      email: '',
      description: '',
      is_enabled: true
    })

    // 加载设置
    const loadSettings = () => {
      // 从localStorage加载邮件通知设置
      const emailEnabled = localStorage.getItem('emailNotificationEnabled')
      emailNotificationEnabled.value = emailEnabled === 'true'

      // 从后端加载最新设置
      loadSettingsFromServer()
    }

    // 从服务器加载设置
    const loadSettingsFromServer = async () => {
      try {
        const response = await fetch(`${API_BASE_URL_WITHOUT_API}/api/notification-settings/`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          }
        })

        if (response.ok) {
          const result = await response.json()
          if (result.success && result.data) {
            if (result.data.email_enabled !== undefined) {
              emailNotificationEnabled.value = result.data.email_enabled
              localStorage.setItem('emailNotificationEnabled', result.data.email_enabled.toString())
            }

            // 加载所有邮箱设置
            if (result.data.all_emails && Array.isArray(result.data.all_emails)) {
              allEmails.value = result.data.all_emails
            }
          }
        }
      } catch (error) {
        console.error('加载服务器设置失败:', error)
        ElMessage.error('从服务器加载设置失败，请刷新页面重试')
      }
    }

    // 保存邮件通知设置
    const saveEmailNotificationSetting = async () => {
      try {
        localStorage.setItem('emailNotificationEnabled', emailNotificationEnabled.value.toString())

        // 后端接口期望收到完整的邮箱列表，所以我们把现有列表一起发过去
        const emailsToUpdate = allEmails.value.map(item => ({
          email: item.email,
          description: item.description,
          is_enabled: item.is_enabled
        }))

        const response = await fetch(`${API_BASE_URL_WITHOUT_API}/api/notification-settings/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            notification_emails: emailsToUpdate,
            email_enabled: emailNotificationEnabled.value
          })
        })

        if (response.ok) {
          const result = await response.json()
          if (result.success) {
            ElMessage.success(`邮件通知已${emailNotificationEnabled.value ? '开启' : '关闭'}并同步到服务器`)
            // 重新从服务器加载，确保状态一致
            loadSettingsFromServer()
          } else {
            ElMessage.error(`保存失败: ${result.error}`)
          }
        } else {
          throw new Error('服务器响应错误')
        }
      } catch (error) {
        console.error('保存通知设置失败:', error)
        ElMessage.warning('设置已保存到本地，但同步到服务器失败')
      }
    }

    // 切换单个邮箱启用状态
    const toggleEmailStatus = async (emailId, isEnabled) => {
      try {
        // [关键修改] 请求发送到后端的 toggle_email_status 视图对应的 URL
        // 你需要在 urls.py 中为 toggle_email_status 视图配置一个 URL，例如 'api/toggle-email-status/'
        const response = await fetch(`${API_BASE_URL_WITHOUT_API}/api/toggle-email-status/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email_id: emailId,
            is_enabled: isEnabled
          })
        })

        if (response.ok) {
          const result = await response.json()
          if (result.success) {
            ElMessage.success(`邮箱已${isEnabled ? '启用' : '禁用'}`)
            // 操作成功后，从服务器重新加载所有邮箱，以确保数据同步
            loadSettingsFromServer()
          } else {
            ElMessage.error(`操作失败: ${result.error}`)
            // 操作失败时，也重新加载，以恢复到服务器上的真实状态
            loadSettingsFromServer()
          }
        } else {
          throw new Error('服务器响应错误')
        }
      } catch (error) {
        console.error('更新邮箱状态失败:', error)
        ElMessage.error('同步服务器失败，请刷新页面')
        loadSettingsFromServer()
      }
    }

    // 添加新邮箱
    const addNewEmail = async () => {
      if (!newEmail.value.email) {
        ElMessage.error('邮箱地址不能为空')
        return
      }
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(newEmail.value.email.trim())) {
        ElMessage.error('请输入有效的邮箱地址')
        return
      }

      try {
        // [关键修改] 构造一个包含所有现有邮箱和新邮箱的完整列表
        const updatedEmailList = allEmails.value.map(e => ({
          email: e.email,
          description: e.description,
          is_enabled: e.is_enabled
        }))

        updatedEmailList.push({
          email: newEmail.value.email.trim(),
          description: newEmail.value.description,
          is_enabled: newEmail.value.is_enabled
        })

        // [关键修改] 将这个完整的列表发送给后端
        const response = await fetch(`${API_BASE_URL_WITHOUT_API}/api/notification-settings/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            notification_emails: updatedEmailList,
            email_enabled: emailNotificationEnabled.value // 别忘了带上总开关的状态
          })
        })

        if (response.ok) {
          const result = await response.json()
          if (result.success) {
            ElMessage.success('新邮箱已添加')
            // 清空输入框
            newEmail.value.email = ''
            newEmail.value.description = ''
            newEmail.value.is_enabled = true
            // [关键修改] 从服务器重新加载所有设置，以获取包含新邮箱 ID 的完整列表
            loadSettingsFromServer()
          } else {
            ElMessage.error(`添加失败: ${result.error}`)
          }
        } else {
          throw new Error('服务器响应错误')
        }
      } catch (error) {
        console.error('添加新邮箱失败:', error)
        ElMessage.error('添加新邮箱失败，请稍后重试')
      }
    }

    // 删除现有邮箱
    const removeExistingEmail = async (emailId) => {
      try {
        // [关键修改] 构造一个不包含要删除邮箱的新列表
        const updatedEmailList = allEmails.value
            .filter(item => item.id !== emailId)
            .map(e => ({
              email: e.email,
              description: e.description,
              is_enabled: e.is_enabled
            }))

        // [关键修改] 将这个新列表发送给后端进行批量更新
        const response = await fetch(`${API_BASE_URL_WITHOUT_API}/api/notification-settings/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            notification_emails: updatedEmailList,
            email_enabled: emailNotificationEnabled.value // 别忘了带上总开关的状态
          })
        })

        if (response.ok) {
          const result = await response.json()
          if (result.success) {
            ElMessage.success('邮箱已删除')
            // [关键修改] 从服务器重新加载，确保列表同步
            loadSettingsFromServer()
          } else {
            ElMessage.error(`删除失败: ${result.error}`)
          }
        } else {
          throw new Error('服务器响应错误')
        }
      } catch (error) {
        console.error('删除邮箱失败:', error)
        ElMessage.error('删除邮箱失败，请稍后重试')
      }
    }

    onMounted(() => {
      loadSettings()
    })

    return {
      emailNotificationEnabled,
      allEmails,
      newEmail,
      saveEmailNotificationSetting,
      toggleEmailStatus,
      removeExistingEmail,
      addNewEmail
    }
  }
}
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.settings-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.settings-header {
  margin-bottom: 20px;
}

.settings-header h2 {
  color: #303133;
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.setting-card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-bottom: 1px solid #f0f2f5;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-label {
  flex: 1;
}

.setting-label span {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.setting-desc {
  font-size: 14px;
  color: #909399;
  margin: 4px 0 0 0;
}

.setting-control {
  display: flex;
  align-items: center;
}

.email-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.email-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.content-section {
  padding: 0;
  line-height: 1.6;
}

.content-section h3 {
  color: #409eff;
  font-size: 18px;
  margin: 20px 0 10px 0;
  border-left: 4px solid #409eff;
  padding-left: 12px;
}

.content-section p {
  margin: 10px 0;
  color: #606266;
  font-size: 14px;
}

.content-section ul,
.content-section ol {
  margin: 10px 0;
  padding-left: 20px;
  color: #606266;
}

.content-section li {
  margin: 5px 0;
  font-size: 14px;
}

.disclaimer {
  background-color: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 4px;
  padding: 15px;
  margin: 15px 0;
}

.disclaimer p {
  color: #f56c6c;
  font-weight: 600;
  margin-bottom: 8px;
}

.disclaimer ul {
  margin: 0;
}

.disclaimer li {
  color: #606266;
}

/* 邮箱管理样式 */
.email-management-section {
  width: 100%;
  margin-bottom: 20px;
}

.email-management-section h4 {
  color: #409eff;
  font-size: 16px;
  margin: 0 0 10px 0;
  font-weight: 600;
}

.existing-emails {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.email-management-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.email-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.email-address {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.email-description {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.email-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.new-email-form {
  width: 100%;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.delete-email-btn {
  padding: 6px 12px !important;
  font-size: 12px !important;
  height: 28px !important;
  border-radius: 4px !important;
  background-color: #f56c6c !important;
  border-color: #f56c6c !important;
  color: #fff !important;
  transition: all 0.3s ease !important;
  display: flex !important;
  align-items: center !important;
  gap: 4px !important;
}

.delete-email-btn:hover {
  background-color: #f04747 !important;
  border-color: #f04747 !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 2px 4px rgba(245, 108, 108, 0.3) !important;
}

.delete-email-btn:active {
  transform: translateY(0) !important;
  box-shadow: 0 1px 2px rgba(245, 108, 108, 0.2) !important;
}

.delete-email-btn .el-icon {
  font-size: 12px !important;
}

/* 暗色主题下的删除按钮样式 */
.dark .delete-email-btn {
  background-color: #dc2626 !important;
  border-color: #dc2626 !important;
}

.dark .delete-email-btn:hover {
  background-color: #b91c1c !important;
  border-color: #b91c1c !important;
  box-shadow: 0 2px 4px rgba(220, 38, 38, 0.4) !important;
}

.dark .delete-email-btn:active {
  box-shadow: 0 1px 2px rgba(220, 38, 38, 0.3) !important;
}

/* 暗色主题 */
.dark .settings-page {
  background-color: #141414;
}

.dark .settings-header h2 {
  color: #e5e7eb;
}

.dark .setting-card {
  background-color: #1f1f1f;
  border-color: #434343;
}

.dark .card-header {
  color: #e5e7eb;
}

.dark .setting-label span {
  color: #e5e7eb;
}

.dark .setting-desc {
  color: #9ca3af;
}

.dark .content-section h3 {
  color: #60a5fa;
}

.dark .content-section p,
.dark .content-section li {
  color: #d1d5db;
}
</style>
