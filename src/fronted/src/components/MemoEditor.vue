<template>
  <div class="memo-editor">
    <div v-if="!memo" class="empty-editor">
      <el-empty description="选择一个备忘录开始编辑，或创建新的备忘录" />
    </div>

    <div v-else class="editor-container">
      <!-- 标题输入区域 -->
      <div class="editor-header">
        <el-input
          v-model="localMemo.title"
          placeholder="输入标题..."
          class="title-input"
          @input="handleTitleChange"
          :disabled="loading"
          clearable
        />
        <div class="editor-actions">
          <el-button
            :loading="loading"
            @click="handleSave"
            type="primary"
            size="small"
            :disabled="!hasUnsavedChanges"
            :icon="hasUnsavedChanges ? 'DocumentAdd' : 'Check'"
          >
            {{ hasUnsavedChanges ? '保存' : '已保存' }}
          </el-button>
        </div>
      </div>

      <!-- 编辑器主体 -->
      <div class="editor-content">
        <el-tabs v-model="activeTab" class="memo-tabs" @tab-change="handleTabChange">
          <!-- 编辑模式 -->
          <el-tab-pane label="编辑" name="edit">
            <div class="editor-toolbar">
              <el-upload
                :show-file-list="false"
                :before-upload="handleImageUpload"
                accept="image/*"
                class="image-upload"
                :disabled="!memo?.id || loading"
              >
                <el-button size="small" :icon="Picture" :disabled="!memo?.id || loading">
                  插入图片
                </el-button>
              </el-upload>
              <el-divider direction="vertical" />
              <el-button size="small" @click="insertMarkdown('**', '**')" :disabled="loading">
                <strong>B</strong>
              </el-button>
              <el-button size="small" @click="insertMarkdown('*', '*')" :disabled="loading">
                <em>I</em>
              </el-button>
              <el-button size="small" @click="insertMarkdown('`', '`')" :disabled="loading">
                <code>&lt;/&gt;</code>
              </el-button>
              <el-button size="small" @click="insertMarkdown('# ', '')" :disabled="loading">
                H1
              </el-button>
              <el-button size="small" @click="insertMarkdown('## ', '')" :disabled="loading">
                H2
              </el-button>
            </div>

            <el-input
              v-model="localMemo.content"
              type="textarea"
              placeholder="开始输入内容... 支持 Markdown 语法
                          提示：
                          - 可直接粘贴图片
                          - 支持 Ctrl+S 保存
                          - 支持 Tab 键缩进
                          - 支持拖拽图片上传"
              class="content-textarea"
              @paste="handlePaste"
              @input="handleContentChange"
              @keydown="handleKeydown"
              @drop="handleDrop"
              @dragover="handleDragOver"
              resize="none"
              ref="textareaRef"
              :disabled="loading"
            />
          </el-tab-pane>

          <!-- 预览模式 -->
          <el-tab-pane label="预览" name="preview">
            <div class="preview-container">
              <div class="preview-header">
                <h2 v-if="localMemo.title" class="preview-title">{{ localMemo.title }}</h2>
                <div class="preview-meta">
                  <el-tag size="small" type="info">预览模式</el-tag>
                  <span class="word-count">{{ contentLength }} 字符</span>
                </div>
              </div>
              <div class="preview-content" v-html="renderedContent"></div>
            </div>
          </el-tab-pane>

          <!-- 分屏模式 -->
          <el-tab-pane label="分屏" name="split">
            <div class="split-view" ref="splitViewRef">
              <div
                class="split-editor"
                :style="{ width: `${splitLeftWidth}%` }"
              >
                <div class="split-header">
                  <span>编辑</span>
                  <el-tag size="small">{{ contentLength }} 字符</el-tag>
                </div>
                <el-input
                  v-model="localMemo.content"
                  type="textarea"
                  placeholder="编写内容..."
                  class="split-textarea"
                  @paste="handlePaste"
                  @input="handleContentChange"
                  @scroll="syncScroll"
                  @keydown="handleKeydown"
                  @drop="handleDrop"
                  @dragover="handleDragOver"
                  resize="none"
                  ref="splitTextareaRef"
                  :disabled="loading"
                />
              </div>
              <div
                class="split-divider"
                @mousedown="startResize"
                :class="{ 'dragging': isDragging }"
              ></div>
              <div
                class="split-preview"
                :style="{ width: `${100 - splitLeftWidth}%` }"
              >
                <div class="split-header">
                  <span>预览</span>
                  <el-tag size="small" type="success">实时渲染</el-tag>
                </div>
                <div
                  class="split-preview-content"
                  v-html="renderedContent"
                  ref="splitPreviewRef"
                  @scroll="syncPreviewScroll"
                ></div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 状态栏 -->
      <div class="editor-footer">
        <div class="memo-info">
          <span class="word-count">字符: {{ contentLength }}</span>
          <el-divider direction="vertical" />
          <span class="status-indicator">
            <el-tag v-if="autoSaveStatus === 'saving'" type="info" size="small" class="auto-save-tag">
              <el-icon class="is-loading"><Loading /></el-icon>
              自动保存中...
            </el-tag>
            <el-tag v-else-if="autoSaveStatus === 'saved'" type="success" size="small" class="auto-save-tag">
              <el-icon><Check /></el-icon>
              已自动保存
            </el-tag>
            <el-tag v-else-if="autoSaveStatus === 'error'" type="danger" size="small" class="auto-save-tag">
              <el-icon><Close /></el-icon>
              保存失败
            </el-tag>
            <el-tag v-else-if="hasUnsavedChanges" type="warning" size="small" :icon="Edit">
              未保存
            </el-tag>
            <el-tag v-else type="success" size="small" :icon="Check">
              已保存
            </el-tag>
          </span>
          <el-divider direction="vertical" />
          <span class="create-time">创建: {{ formatDate(memo?.created_at) }}</span>
          <span v-if="memo?.updated_at && memo.updated_at !== memo?.created_at" class="update-time">
            · 更新: {{ formatDate(memo.updated_at) }}
          </span>
          <div class="spacer"></div>
          <el-button
            v-if="hasUnsavedChanges && autoSaveStatus !== 'saving'"
            @click="discardChanges"
            size="small"
            type="info"
            plain
          >
            取消更改
          </el-button>
        </div>
      </div>
    </div>

    <!-- 图片预览弹窗 -->
    <el-dialog
      v-model="imagePreviewVisible"
      title="图片预览"
      width="80%"
      center
      :close-on-click-modal="true"
    >
      <div class="image-preview-dialog">
        <img
          :src="previewImageUrl"
          alt="预览图片"
          class="preview-image"
          @error="handleImageError"
        />
      </div>
      <template #footer>
        <el-button @click="imagePreviewVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 图片上传进度 -->
    <el-dialog v-model="uploadProgressVisible" title="上传进度" width="400px" :close-on-click-modal="false">
      <div class="upload-progress">
        <el-progress :percentage="uploadProgress" :status="uploadStatus"></el-progress>
        <p class="upload-text">{{ uploadText }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, watch, nextTick, onMounted, onUnmounted, getCurrentInstance } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Picture, Edit, Check, DocumentAdd, Loading, Close } from '@element-plus/icons-vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { API_BASE_URL_WITHOUT_API } from '@/services/api'

export default {
  name: 'MemoEditor',
  components: {
    Picture,
    Edit,
    Check,
    DocumentAdd,
    Loading,
    Close
  },
  props: {
    memo: {
      type: Object,
      default: null
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['save', 'upload-image'],
  setup(props, { emit }) {
    const instance = getCurrentInstance()

    // 响应式状态
    const activeTab = ref('edit')
    const localMemo = ref({
      id: null,
      title: '',
      content: '',
      created_at: null,
      updated_at: null
    })
    const originalMemo = ref({})

    // DOM 引用
    const textareaRef = ref(null)
    const splitTextareaRef = ref(null)
    const splitPreviewRef = ref(null)

    // 图片预览状态
    const imagePreviewVisible = ref(false)
    const previewImageUrl = ref('')

    // 上传进度状态
    const uploadProgressVisible = ref(false)
    const uploadProgress = ref(0)
    const uploadStatus = ref('')
    const uploadText = ref('')

    // 自动保存状态
    const autoSaveStatus = ref('') // 'saving', 'saved', 'error', ''

    // 定时器引用
    let autoSaveTimer = null
    let debounceTimer = null
    let autoSaveStatusTimer = null
    const splitViewRef = ref(null)
    const splitLeftWidth = ref(50) // 左侧面板宽度百分比
    const isDragging = ref(false)
    const startX = ref(0)
    const startLeftWidth = ref(50)

    // 计算属性
    const hasUnsavedChanges = computed(() => {
      if (!originalMemo.value || !localMemo.value) return false
      return (
        localMemo.value.title !== originalMemo.value.title ||
        localMemo.value.content !== originalMemo.value.content
      )
    })

    const contentLength = computed(() => {
      return localMemo.value?.content ? localMemo.value.content.length : 0
    })

    const renderedContent = computed(() => {
      if (!localMemo.value?.content) {
        return '<div class="empty-preview">暂无内容</div>'
      }

      try {
        // 配置 marked 选项
        marked.setOptions({
          breaks: true,
          gfm: true,
          headerIds: false,
          mangle: false
        })

        let html = marked.parse(localMemo.value.content)

        // 处理图片链接
        html = html.replace(/<img([^>]+)src="([^"]+)"/g, (match, attributes, src) => {
          let fullSrc = src
          if (!src.startsWith('http') && !src.startsWith('data:')) {
            fullSrc = src.startsWith('/') ? `${API_BASE_URL_WITHOUT_API}${src}` : src
          }
          return `<img${attributes}src="${fullSrc}" onclick="window.previewMemoImage('${fullSrc}')" loading="lazy"`
        })

        // 清理 HTML 但保留必要的属性
        return DOMPurify.sanitize(html, {
          ADD_ATTR: ['onclick', 'loading'],
          ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'onclick', 'loading', 'class']
        })
      } catch (error) {
        console.error('Markdown 渲染错误:', error)
        return '<div class="error-preview">内容渲染失败，请检查 Markdown 语法</div>'
      }
    })

    // 方法定义
    const handleTitleChange = () => {
      debounceInput()
    }

    const handleContentChange = () => {
      debounceInput()
    }

    const debounceInput = () => {
      clearTimeout(debounceTimer)
      clearTimeout(autoSaveTimer) // 清除之前的自动保存计划

      debounceTimer = setTimeout(() => {
        if (hasUnsavedChanges.value && props.memo?.id) {
          scheduleAutoSave()
        }
      }, 2000) // 用户停止输入2秒后考虑自动保存
    }

    const scheduleAutoSave = () => {
      clearTimeout(autoSaveTimer)
      autoSaveTimer = setTimeout(() => {
        if (hasUnsavedChanges.value && props.memo?.id) {
          // 检查用户是否仍在编辑
          const activeElement = document.activeElement
          const isUserEditing = activeElement &&
            (activeElement.tagName === 'TEXTAREA' ||
             activeElement.tagName === 'INPUT' ||
             activeElement.isContentEditable)

          if (!isUserEditing) {
            handleSave(true) // 自动保存
          } else {
            // 如果用户仍在编辑，延迟自动保存
            scheduleAutoSave()
          }
        }
      }, 5000) // 增加到5秒，减少打断频率
    }

    const handleSave = async (isAutoSave = false) => {
      if (!localMemo.value.title?.trim() && !localMemo.value.content?.trim()) {
        if (!isAutoSave) {
          ElMessage.warning('标题和内容不能都为空')
        }
        return
      }

      // 显示保存状态
      if (isAutoSave) {
        autoSaveStatus.value = 'saving'
      }

      try {
        const memoData = {
          ...localMemo.value,
          title: localMemo.value.title?.trim() || '无标题',
          content: localMemo.value.content || ''
        }

        await emit('save', memoData, isAutoSave)

        // 更新原始数据
        originalMemo.value = { ...memoData }

        if (isAutoSave) {
          autoSaveStatus.value = 'saved'
          // 2秒后清除保存状态提示
          clearTimeout(autoSaveStatusTimer)
          autoSaveStatusTimer = setTimeout(() => {
            autoSaveStatus.value = ''
          }, 2000)
        } else {
          ElMessage.success('保存成功')
        }
      } catch (error) {
        console.error('保存失败:', error)
        if (isAutoSave) {
          autoSaveStatus.value = 'error'
          // 3秒后清除错误状态提示
          clearTimeout(autoSaveStatusTimer)
          autoSaveStatusTimer = setTimeout(() => {
            autoSaveStatus.value = ''
          }, 3000)
        } else {
          ElMessage.error('保存失败，请稍后重试')
        }
      }
    }

    const handleImageUpload = async (file) => {
      if (!props.memo?.id) {
        ElMessage.warning('请先保存备忘录再上传图片')
        return false
      }

      // 验证文件类型
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml']
      if (!allowedTypes.includes(file.type)) {
        ElMessage.error('只支持 JPG、PNG、GIF、WebP、SVG 格式的图片')
        return false
      }

      // 验证文件大小 (10MB)
      const maxSize = 10 * 1024 * 1024
      if (file.size > maxSize) {
        ElMessage.error('图片大小不能超过 10MB')
        return false
      }

      // 显示上传进度
      showUploadProgress('正在上传图片...')

      try {
        await emit('upload-image', file, props.memo.id)
        hideUploadProgress()
      } catch (error) {
        hideUploadProgress()
        console.error('图片上传失败:', error)
      }

      return false
    }

    const handlePaste = async (event) => {
      const items = event.clipboardData?.items
      if (!items) return

      for (let item of items) {
        if (item.type.indexOf('image') !== -1) {
          event.preventDefault()

          if (!props.memo?.id) {
            ElMessage.warning('请先保存备忘录再粘贴图片')
            return
          }

          const file = item.getAsFile()
          if (file) {
            await handleImageUpload(file)
          }
          break
        }
      }
    }

    const handleDrop = async (event) => {
      event.preventDefault()

      if (!props.memo?.id) {
        ElMessage.warning('请先保存备忘录再拖拽图片')
        return
      }

      const files = Array.from(event.dataTransfer.files)
      const imageFiles = files.filter(file => file.type.startsWith('image/'))

      if (imageFiles.length === 0) {
        ElMessage.warning('请拖拽图片文件')
        return
      }

      // 批量上传
      for (const file of imageFiles) {
        await handleImageUpload(file)
      }
    }

    const handleDragOver = (event) => {
      event.preventDefault()
    }

    const insertMarkdown = (before, after = '') => {
      const textarea = getActiveTextarea()
      if (!textarea) return

      const start = textarea.selectionStart || 0
      const end = textarea.selectionEnd || 0
      const content = localMemo.value?.content || ''
      const selectedText = content.substring(start, end)

      let newText
      if (selectedText && after) {
        newText = `${before}${selectedText}${after}`
      } else {
        newText = `${before}${selectedText}`
      }

      localMemo.value.content = content.substring(0, start) + newText + content.substring(end)

      nextTick(() => {
        if (textarea && textarea.focus && textarea.setSelectionRange) {
          textarea.focus()
          const newPos = after ? start + before.length : start + newText.length
          textarea.setSelectionRange(newPos, newPos)
        }
      })

      handleContentChange()
    }

    const getActiveTextarea = () => {
      if (activeTab.value === 'split') {
        return splitTextareaRef.value?.$refs?.textarea || null
      }
      return textareaRef.value?.$refs?.textarea || null
    }

    const handleKeydown = (event) => {
      // Ctrl+S 保存
      if (event.ctrlKey && event.key === 's') {
        event.preventDefault()
        handleSave()
        return
      }

      // Tab 键缩进
      if (event.key === 'Tab') {
        event.preventDefault()
        const textarea = event.target
        if (!textarea) return

        const start = textarea.selectionStart || 0
        const end = textarea.selectionEnd || 0
        const content = localMemo.value?.content || ''

        localMemo.value.content = content.substring(0, start) + '  ' + content.substring(end)

        nextTick(() => {
          if (textarea && textarea.setSelectionRange) {
            textarea.setSelectionRange(start + 2, start + 2)
          }
        })

        handleContentChange()
      }
    }

    // 拖拽调整功能
    const startResize = (event) => {
      event.preventDefault()
      event.stopPropagation()

      isDragging.value = true
      startX.value = event.clientX
      startLeftWidth.value = splitLeftWidth.value

      // 检测当前是否为垂直布局
      const isVerticalLayout = window.innerWidth <= 1200

      if (isVerticalLayout) {
        document.body.style.cursor = 'row-resize'
      } else {
        document.body.style.cursor = 'col-resize'
      }

      document.body.style.userSelect = 'none'

      document.addEventListener('mousemove', handleResize)
      document.addEventListener('mouseup', stopResize)
    }

    const handleResize = (event) => {
      if (!isDragging.value || !splitViewRef.value) return

      // 检测当前是否为垂直布局
      const isVerticalLayout = window.innerWidth <= 1200

      if (isVerticalLayout) {
        // 垂直布局时暂不支持拖拽调整
        return
      }

      try {
        const containerWidth = splitViewRef.value.clientWidth
        const deltaX = event.clientX - startX.value
        const deltaPercent = (deltaX / containerWidth) * 100

        let newLeftWidth = startLeftWidth.value + deltaPercent

        // 限制拖拽范围 (20% - 80%)
        newLeftWidth = Math.max(20, Math.min(80, newLeftWidth))
        splitLeftWidth.value = newLeftWidth

        // 保存到 localStorage
        localStorage.setItem('memoEditorSplitWidth', newLeftWidth.toString())
      } catch (error) {
        console.warn('拖拽调整大小时出现错误:', error)
        // 在出错时停止拖拽
        stopResize()
      }
    }

    const stopResize = () => {
      isDragging.value = false
      document.body.style.cursor = ''
      document.body.style.userSelect = ''

      document.removeEventListener('mousemove', handleResize)
      document.removeEventListener('mouseup', stopResize)
    }

    const syncScroll = (event) => {
      if (activeTab.value !== 'split' || !splitPreviewRef.value) return

      const textarea = event.target
      if (!textarea) return

      const scrollRatio = textarea.scrollTop / (textarea.scrollHeight - textarea.clientHeight)

      if (!isNaN(scrollRatio) && isFinite(scrollRatio)) {
        const previewElement = splitPreviewRef.value
        if (previewElement && previewElement.scrollHeight > previewElement.clientHeight) {
          const maxScroll = previewElement.scrollHeight - previewElement.clientHeight
          previewElement.scrollTop = scrollRatio * maxScroll
        }
      }
    }

    // 滚动同步 - 预览到编辑器
    const syncPreviewScroll = (event) => {
      if (activeTab.value !== 'split' || !splitTextareaRef.value) return

      const previewElement = event.target
      if (!previewElement) return

      const scrollRatio = previewElement.scrollTop / (previewElement.scrollHeight - previewElement.clientHeight)

      if (!isNaN(scrollRatio) && isFinite(scrollRatio)) {
        const textarea = splitTextareaRef.value?.$refs?.textarea
        if (textarea && textarea.scrollHeight > textarea.clientHeight) {
          const maxScroll = textarea.scrollHeight - textarea.clientHeight
          textarea.scrollTop = scrollRatio * maxScroll
        }
      }
    }

    const handleTabChange = (tabName) => {
      activeTab.value = tabName

      // 切换到编辑模式时聚焦文本域
      if (tabName === 'edit') {
        nextTick(() => {
          const textarea = textareaRef.value?.$refs?.textarea
          if (textarea && textarea.focus) {
            textarea.focus()
          }
        })
      }
    }

    const discardChanges = async () => {
      try {
        await ElMessageBox.confirm(
          '确定要取消所有未保存的更改吗？此操作不可撤销。',
          '确认取消更改',
          {
            confirmButtonText: '确定',
            cancelButtonText: '保留更改',
            type: 'warning',
          }
        )

        // 恢复到原始状态
        if (originalMemo.value) {
          localMemo.value = { ...originalMemo.value }
        }
        ElMessage.info('已取消更改')
      } catch {
        // 用户取消
      }
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return '未知时间'

      try {
        const date = new Date(dateStr)
        if (isNaN(date.getTime())) return '无效时间'

        return date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch {
        return '时间格式错误'
      }
    }

    const handleImageError = () => {
      ElMessage.error('图片加载失败')
    }

    const showUploadProgress = (text) => {
      uploadText.value = text
      uploadProgress.value = 0
      uploadStatus.value = ''
      uploadProgressVisible.value = true

      // 模拟进度
      const interval = setInterval(() => {
        uploadProgress.value += Math.random() * 20
        if (uploadProgress.value >= 90) {
          clearInterval(interval)
        }
      }, 200)
    }

    const hideUploadProgress = () => {
      uploadProgress.value = 100
      uploadStatus.value = 'success'
      setTimeout(() => {
        uploadProgressVisible.value = false
      }, 500)
    }

    // 全局图片预览函数
    window.previewMemoImage = (url) => {
      previewImageUrl.value = url
      imagePreviewVisible.value = true
    }

    // 监听器
    watch(() => props.memo, async (newMemo) => {
      // 清除定时器
      clearTimeout(autoSaveTimer)
      clearTimeout(debounceTimer)

      // 等待下一个 tick 确保组件状态稳定
      await nextTick()

      if (newMemo) {
        localMemo.value = { ...newMemo }
        originalMemo.value = { ...newMemo }
      } else {
        localMemo.value = {
          id: null,
          title: '',
          content: '',
          created_at: null,
          updated_at: null
        }
        originalMemo.value = {}
      }
    }, { immediate: true, deep: true })

    // 生命周期
    onMounted(() => {
      // 从 localStorage 恢复分屏宽度
      const savedWidth = localStorage.getItem('memoEditorSplitWidth')
      if (savedWidth) {
        const width = parseFloat(savedWidth)
        if (!isNaN(width) && width >= 20 && width <= 80) {
          splitLeftWidth.value = width
        }
      }

      // 监听窗口关闭前事件
      const handleBeforeUnload = (event) => {
        if (hasUnsavedChanges.value) {
          event.preventDefault()
          event.returnValue = '您有未保存的更改，确定要离开吗？'
          return event.returnValue
        }
      }

      window.addEventListener('beforeunload', handleBeforeUnload)

      // 清理函数
      instance.scope.stop = () => {
        window.removeEventListener('beforeunload', handleBeforeUnload)
        // 清理拖拽事件监听器
        document.removeEventListener('mousemove', handleResize)
        document.removeEventListener('mouseup', stopResize)
      }
    })

    onUnmounted(() => {
      // 清理定时器
      clearTimeout(autoSaveTimer)
      clearTimeout(debounceTimer)
      clearTimeout(autoSaveStatusTimer)

      // 清理全局函数
      delete window.previewMemoImage

      // 执行清理函数
      if (instance.scope.stop) {
        instance.scope.stop()
      }
    })

    return {
      // 响应式状态
      activeTab,
      localMemo,
      splitLeftWidth,
      splitViewRef,
      isDragging,
      autoSaveStatus,

      // DOM 引用
      textareaRef,
      splitTextareaRef,
      splitPreviewRef,

      // 图片预览
      imagePreviewVisible,
      previewImageUrl,

      // 上传进度
      uploadProgressVisible,
      uploadProgress,
      uploadStatus,
      uploadText,

      // 计算属性
      hasUnsavedChanges,
      contentLength,
      renderedContent,

      // 方法
      handleTitleChange,
      handleContentChange,
      handleSave,
      handleImageUpload,
      handlePaste,
      handleDrop,
      handleDragOver,
      insertMarkdown,
      handleKeydown,
      syncScroll,
      syncPreviewScroll,
      startResize,
      handleTabChange,
      discardChanges,
      formatDate,
      handleImageError,

      // 图标
      Picture,
      Edit,
      Check,
      DocumentAdd,
      Loading,
      Close
    }
  }
}
</script>

<style scoped>
.memo-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  position: relative;
}

.empty-editor {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: #f8f9fa;
}

.editor-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 头部区域 */
.editor-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  gap: 12px;
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.title-input {
  flex: 1;
}

.title-input :deep(.el-input__wrapper) {
  border: none;
  box-shadow: none;
  font-size: 18px;
  font-weight: 600;
  padding: 8px 0;
}

.title-input :deep(.el-input__inner) {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.title-input :deep(.el-input__inner)::placeholder {
  color: #c0c4cc;
  font-weight: 400;
}

.editor-actions {
  display: flex;
  gap: 8px;
}

/* 内容区域 */
.editor-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.memo-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.memo-tabs :deep(.el-tabs__header) {
  margin: 0;
  background: #f8f9fa;
  padding: 0 20px;
  border-bottom: 1px solid #e4e7ed;
}

.memo-tabs :deep(.el-tabs__content) {
  flex: 1;
  padding: 0;
  overflow: hidden;
}

.memo-tabs :deep(.el-tab-pane) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 工具栏 */
.editor-toolbar {
  padding: 12px 20px;
  background: #fafbfc;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.image-upload :deep(.el-upload) {
  display: inline-block;
}

/* 文本编辑区域 */
.content-textarea {
  flex: 1;
  margin: 20px;
  min-height: 0;
}

.content-textarea :deep(.el-textarea) {
  height: 100%;
}

.content-textarea :deep(.el-textarea__inner) {
  border: 1px solid #dcdfe6;
  font-family: 'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  resize: none;
  height: 100% !important;
  min-height: 300px;
  transition: border-color 0.2s ease;
}

.content-textarea :deep(.el-textarea__inner):focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.content-textarea :deep(.el-textarea__inner):disabled {
  background-color: #f5f7fa;
  cursor: not-allowed;
}

/* 预览区域 */
.preview-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preview-header {
  padding: 20px 20px 16px;
  border-bottom: 1px solid #e4e7ed;
  background: #ffffff;
}

.preview-title {
  margin: 0 0 12px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1.3;
}

.preview-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.preview-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #ffffff;
  line-height: 1.7;
}

/* 分屏模式 */
.split-view {
  flex: 1;
  display: flex;
  height: 100%;
  position: relative;
}

.split-editor,
.split-preview {
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
  flex-shrink: 0;
  transition: width 0.1s ease;
}

.split-header {
  padding: 12px 16px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  font-size: 12px;
  color: #606266;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.split-textarea {
  flex: 1;
  margin: 0;
  padding: 16px;
  min-height: 300px;
}

.split-textarea :deep(.el-textarea) {
  height: 100%;
}

.split-textarea :deep(.el-textarea__inner) {
  border: 1px solid #dcdfe6;
  font-family: 'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  height: 100% !important;
  resize: none;
  transition: border-color 0.2s ease;
}

.split-textarea :deep(.el-textarea__inner):focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.split-divider {
  width: 8px;
  background: #f5f7fa;
  border-left: 1px solid #e4e7ed;
  border-right: 1px solid #e4e7ed;
  flex-shrink: 0;
  position: relative;
  cursor: col-resize;
  transition: all 0.2s ease;
  z-index: 10;
  user-select: none;
}

.split-divider:hover,
.split-divider.dragging {
  background: #e4e7ed;
  border-color: #409eff;
}

.split-divider.dragging::before {
  background: #409eff;
}

.split-divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 3px;
  height: 24px;
  background: #dcdfe6;
  border-radius: 2px;
  transition: background 0.2s ease;
  pointer-events: none;
}

/* 增加可点击区域 */
.split-divider::after {
  content: '';
  position: absolute;
  top: 0;
  left: -4px;
  right: -4px;
  bottom: 0;
  cursor: col-resize;
}

.split-preview-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  line-height: 1.7;
  background: #ffffff;
}

/* 底部状态栏 */
.editor-footer {
  padding: 12px 20px;
  border-top: 1px solid #e4e7ed;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.05);
}

.memo-info {
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 8px;
}

.word-count {
  font-weight: 500;
  color: #606266;
}

.status-indicator .el-tag {
  margin: 0;
}

.auto-save-tag {
  animation: fadeInOut 0.3s ease-in-out;
}

.auto-save-tag .el-icon.is-loading {
  animation: rotating 1s linear infinite;
}

@keyframes fadeInOut {
  0% { opacity: 0; transform: translateY(-2px); }
  100% { opacity: 1; transform: translateY(0); }
}

@keyframes rotating {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.spacer {
  flex: 1;
}

/* Markdown 预览样式 */
.preview-content :deep(h1),
.preview-content :deep(h2),
.preview-content :deep(h3),
.preview-content :deep(h4),
.preview-content :deep(h5),
.preview-content :deep(h6),
.split-preview-content :deep(h1),
.split-preview-content :deep(h2),
.split-preview-content :deep(h3),
.split-preview-content :deep(h4),
.split-preview-content :deep(h5),
.split-preview-content :deep(h6) {
  color: #303133;
  margin: 1.5em 0 0.8em 0;
  font-weight: 600;
  line-height: 1.3;
}

.preview-content :deep(h1),
.split-preview-content :deep(h1) {
  font-size: 2em;
  border-bottom: 2px solid #e4e7ed;
  padding-bottom: 0.5em;
}

.preview-content :deep(h2),
.split-preview-content :deep(h2) {
  font-size: 1.6em;
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 0.3em;
}

.preview-content :deep(h3),
.split-preview-content :deep(h3) { font-size: 1.3em; }

.preview-content :deep(p),
.split-preview-content :deep(p) {
  margin: 0.8em 0;
  color: #606266;
  text-align: justify;
}

.preview-content :deep(code),
.split-preview-content :deep(code) {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
  color: #e96900;
  border: 1px solid #dcdfe6;
}

.preview-content :deep(pre),
.split-preview-content :deep(pre) {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1.2em 0;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.preview-content :deep(pre code),
.split-preview-content :deep(pre code) {
  background: none;
  padding: 0;
  border: none;
  color: #303133;
}

.preview-content :deep(blockquote),
.split-preview-content :deep(blockquote) {
  border-left: 4px solid #409eff;
  margin: 1.2em 0;
  padding: 0.8em 0 0.8em 1.2em;
  background: rgba(64, 158, 255, 0.05);
  border-radius: 0 4px 4px 0;
  color: #606266;
  font-style: italic;
}

.preview-content :deep(ul),
.preview-content :deep(ol),
.split-preview-content :deep(ul),
.split-preview-content :deep(ol) {
  padding-left: 2em;
  margin: 1em 0;
}

.preview-content :deep(li),
.split-preview-content :deep(li) {
  margin: 0.5em 0;
  line-height: 1.6;
}

.preview-content :deep(img),
.split-preview-content :deep(img) {
  max-width: 100%;
  width: auto;
  height: auto;
  max-height: 400px;
  border-radius: 8px;
  margin: 1.2em 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e4e7ed;
  display: block;
  object-fit: contain;
}

.preview-content :deep(img:hover),
.split-preview-content :deep(img:hover) {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.preview-content :deep(table),
.split-preview-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1.2em 0;
  background: #ffffff;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.preview-content :deep(th),
.preview-content :deep(td),
.split-preview-content :deep(th),
.split-preview-content :deep(td) {
  border: 1px solid #e4e7ed;
  padding: 12px 16px;
  text-align: left;
}

.preview-content :deep(th),
.split-preview-content :deep(th) {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  font-weight: 600;
  color: #303133;
}

.preview-content :deep(tr:nth-child(even)),
.split-preview-content :deep(tr:nth-child(even)) {
  background-color: #fafbfc;
}

/* 状态提示样式 */
.empty-preview {
  text-align: center;
  color: #909399;
  font-style: italic;
  padding: 60px 20px;
  background: #f8f9fa;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  margin: 20px;
  font-size: 14px;
}

.error-preview {
  text-align: center;
  color: #f56c6c;
  font-style: italic;
  padding: 40px 20px;
  background: rgba(245, 108, 108, 0.1);
  border: 2px dashed #f56c6c;
  border-radius: 8px;
  margin: 20px;
}

/* 图片预览弹窗 */
.image-preview-dialog {
  text-align: center;
  max-height: 70vh;
  overflow: auto;
  background: #ffffff;
  border-radius: 8px;
  padding: 20px;
}

.preview-image {
  max-width: 100%;
  max-height: 70vh;
  width: auto;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  object-fit: contain;
  display: block;
  margin: 0 auto;
}

/* 上传进度弹窗 */
.upload-progress {
  text-align: center;
  padding: 20px;
}

.upload-text {
  margin-top: 16px;
  color: #606266;
  font-size: 14px;
}

/* 滚动条美化 */
.preview-content::-webkit-scrollbar,
.split-preview-content::-webkit-scrollbar,
.content-textarea :deep(.el-textarea__inner)::-webkit-scrollbar,
.split-textarea :deep(.el-textarea__inner)::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.preview-content::-webkit-scrollbar-track,
.split-preview-content::-webkit-scrollbar-track,
.content-textarea :deep(.el-textarea__inner)::-webkit-scrollbar-track,
.split-textarea :deep(.el-textarea__inner)::-webkit-scrollbar-track {
  background: #f1f3f4;
  border-radius: 3px;
}

.preview-content::-webkit-scrollbar-thumb,
.split-preview-content::-webkit-scrollbar-thumb,
.content-textarea :deep(.el-textarea__inner)::-webkit-scrollbar-thumb,
.split-textarea :deep(.el-textarea__inner)::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #c1c1c1 0%, #a8a8a8 100%);
  border-radius: 3px;
  transition: background 0.2s ease;
}

.preview-content::-webkit-scrollbar-thumb:hover,
.split-preview-content::-webkit-scrollbar-thumb:hover,
.content-textarea :deep(.el-textarea__inner)::-webkit-scrollbar-thumb:hover,
.split-textarea :deep(.el-textarea__inner)::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #a8a8a8 0%, #888888 100%);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .split-view {
    flex-direction: column;
  }

  .split-editor,
  .split-preview {
    width: 100% !important;
    min-height: 300px;
  }

  .split-divider {
    width: 100%;
    height: 4px;
    cursor: row-resize;
    background: linear-gradient(to right, transparent, #e4e7ed 20%, #e4e7ed 80%, transparent);
    border: none;
    border-top: 1px solid #e4e7ed;
    border-bottom: 1px solid #e4e7ed;
  }

  .split-divider::before {
    width: 24px;
    height: 3px;
  }

  .split-divider:hover,
  .split-divider.dragging {
    background: linear-gradient(to right, transparent, #409eff 20%, #409eff 80%, transparent);
    border-color: #409eff;
  }
}

@media (max-width: 768px) {
  .editor-header {
    padding: 12px 16px;
    flex-direction: column;
    gap: 12px;
  }

  .title-input {
    width: 100%;
  }

  .editor-toolbar {
    padding: 8px 16px;
    flex-wrap: wrap;
  }

  .content-textarea,
  .split-textarea {
    margin: 12px;
  }

  .preview-content,
  .split-preview-content {
    padding: 16px 12px;
  }

  .memo-info {
    flex-wrap: wrap;
    gap: 4px;
  }

  .spacer {
    display: none;
  }
}

/* 确保明亮主题的样式 */
.memo-editor {
  background: #ffffff !important;
  color: #303133 !important;
}

.editor-header {
  background: #ffffff !important;
  border-bottom: 1px solid #e4e7ed !important;
}

.content-textarea :deep(.el-textarea__inner),
.split-textarea :deep(.el-textarea__inner) {
  background: #ffffff !important;
  border: 1px solid #dcdfe6 !important;
  color: #303133 !important;
}

.preview-content,
.split-preview-content {
  background: #ffffff !important;
  color: #303133 !important;
}

.memo-tabs :deep(.el-tabs__header) {
  background: #f8f9fa !important;
  border-bottom: 1px solid #e4e7ed !important;
}

.editor-toolbar {
  background: #fafbfc !important;
  border-bottom: 1px solid #e4e7ed !important;
}

.editor-footer {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
  border-top: 1px solid #e4e7ed !important;
}

.split-header {
  background: #f5f7fa !important;
  border-bottom: 1px solid #e4e7ed !important;
  color: #606266 !important;
}

.preview-header {
  background: #ffffff !important;
  border-bottom: 1px solid #e4e7ed !important;
}

/* 动画效果 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 焦点指示器 */
.content-textarea :deep(.el-textarea__inner):focus,
.split-textarea :deep(.el-textarea__inner):focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

/* 加载状态 */
.editor-container.loading {
  pointer-events: none;
  opacity: 0.7;
}

.editor-container.loading::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(2px);
  z-index: 999;
}
</style>