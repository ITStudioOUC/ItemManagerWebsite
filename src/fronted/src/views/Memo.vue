<template>
  <AppHeader />
  <div class="memo-container">
    <div class="memo-sidebar">
      <MemoList
        :memos="memos"
        :loading="loading"
        :search-text="searchText"
        @search="handleSearch"
        @select="handleSelectMemo"
        @create="handleCreateMemo"
        @delete="handleDeleteMemo"
        :selected-memo-id="selectedMemoId"
      />
    </div>
    <div class="memo-editor">
      <MemoEditor
        :memo="selectedMemo"
        :loading="editorLoading"
        @save="handleSaveMemo"
        @upload-image="handleUploadImage"
      />
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import MemoList from '../components/MemoList.vue'
import MemoEditor from '../components/MemoEditor.vue'
import { memoService } from '@/services/api'
import { API_BASE_URL_WITHOUT_API } from '@/services/api'
import AppHeader from "@/components/AppHeader.vue";

export default {
  name: 'Memo',
  components: {
    AppHeader,
    MemoList,
    MemoEditor
  },
  setup() {
    const memos = ref([])
    const selectedMemo = ref(null)
    const selectedMemoId = ref(null)
    const loading = ref(false)
    const editorLoading = ref(false)
    const searchText = ref('')

    const loadMemos = async (search = '') => {
      try {
        loading.value = true
        const response = await memoService.getMemos(search)
        memos.value = response.data.results || response.data
      } catch (error) {
        console.error('加载备忘录失败:', error)
        ElMessage.error('加载备忘录失败')
      } finally {
        loading.value = false
      }
    }

    const handleSearch = (text) => {
      searchText.value = text
      loadMemos(text)
    }

    const handleSelectMemo = async (memo) => {
      if (selectedMemoId.value === memo.id) return

      try {
        editorLoading.value = true
        selectedMemoId.value = memo.id
        const response = await memoService.getMemo(memo.id)
        selectedMemo.value = response.data
      } catch (error) {
        console.error('加载备忘录详情失败:', error)
        ElMessage.error('加载备忘录详情失败')
      } finally {
        editorLoading.value = false
      }
    }

    const handleCreateMemo = async () => {
      try {
        // 先清空当前选择
        selectedMemo.value = null
        selectedMemoId.value = null

        // 等待下一个 tick 确保 DOM 更新完成
        await nextTick()

        const newMemo = {
          id: null,
          title: '新建备忘录',
          content: '',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }

        selectedMemo.value = newMemo
      } catch (error) {
        console.error('创建新备忘录失败:', error)
        ElMessage.error('创建新备忘录失败')
      }
    }

    const handleSaveMemo = async (memo, isAutoSave = false) => {
      try {
        editorLoading.value = true
        let response
        const isNewMemo = !memo.id || memo.id === null || memo.id === undefined

        if (isNewMemo) {
          response = await memoService.createMemo(memo)
          selectedMemoId.value = response.data.id
        } else {
          response = await memoService.updateMemo(memo.id, memo)
        }

        selectedMemo.value = response.data

        // 只在手动保存时显示成功消息
        if (!isAutoSave) {
          ElMessage.success('保存成功')
        }

        // 只在创建新备忘录或手动保存时重新加载列表
        // 自动保存时避免重新加载以保持用户的滚动位置和焦点
        if (isNewMemo || !isAutoSave) {
          await loadMemos(searchText.value)
        } else {
          // 自动保存时只更新当前备忘录在列表中的显示（如果需要的话）
          const memoIndex = memos.value.findIndex(m => m.id === memo.id)
          if (memoIndex !== -1) {
            // 更新列表中的备忘录信息，但不重新加载整个列表
            memos.value[memoIndex] = {
              ...memos.value[memoIndex],
              title: response.data.title,
              content_preview: response.data.content?.substring(0, 100) || '',
              updated_at: response.data.updated_at
            }
          }
        }
      } catch (error) {
        console.error('保存备忘录失败:', error)
        ElMessage.error('保存失败')
      } finally {
        editorLoading.value = false
      }
    }

    const handleDeleteMemo = async (memoId) => {
      try {
        await memoService.deleteMemo(memoId)
        ElMessage.success('删除成功')

        // 如果删除的是当前选中的备忘录，清空编辑器
        if (selectedMemoId.value === memoId) {
          selectedMemo.value = null
          selectedMemoId.value = null
        }

        // 重新加载列表
        await loadMemos(searchText.value)
      } catch (error) {
        console.error('删除备忘录失败:', error)
        ElMessage.error('删除失败')
      }
    }

    const handleUploadImage = async (file, memoId) => {
      try {
        const response = await memoService.uploadImage(memoId, file)

        // 上传成功后，将图片插入到编辑器中
        if (response.data && response.data.image) {
          // 确保图片路径是完整的URL
          const imageUrl = response.data.image.startsWith('http')
            ? response.data.image
            : `${API_BASE_URL_WITHOUT_API}${response.data.image}`
          const imageMarkdown = `![${file.name}](${imageUrl})\n`

          // 找到文本域并插入图片标记
          const textarea = document.querySelector('.content-textarea textarea')
          if (textarea && textarea.parentNode) {
            const start = textarea.selectionStart || textarea.value.length
            const end = textarea.selectionEnd || textarea.value.length
            const currentContent = selectedMemo.value.content || ''

            selectedMemo.value.content =
              currentContent.substring(0, start) +
              imageMarkdown +
              currentContent.substring(end)

            // 更新光标位置
            setTimeout(() => {
              if (textarea && textarea.parentNode && textarea.focus && textarea.setSelectionRange) {
                textarea.focus()
                textarea.setSelectionRange(start + imageMarkdown.length, start + imageMarkdown.length)
              }
            }, 0)
          }

          ElMessage.success('图片上传成功')
        }

        return response.data
      } catch (error) {
        console.error('上传图片失败:', error)
        ElMessage.error('上传图片失败')
        throw error
      }
    }

    onMounted(() => {
      loadMemos()
    })

    return {
      memos,
      selectedMemo,
      selectedMemoId,
      loading,
      editorLoading,
      searchText,
      handleSearch,
      handleSelectMemo,
      handleCreateMemo,
      handleSaveMemo,
      handleDeleteMemo,
      handleUploadImage
    }
  }
}
</script>

<style scoped>
.memo-container {
  display: flex;
  height: calc(100vh - 60px);
  background-color: #f5f5f5;
}

.memo-sidebar {
  width: 350px;
  min-width: 300px;
  border-right: 1px solid #e4e7ed;
  background-color: #ffffff;
  overflow: hidden;
}

.memo-editor {
  flex: 1;
  background-color: #ffffff;
  overflow: hidden;
}

@media (max-width: 768px) {
  .memo-container {
    flex-direction: column;
  }

  .memo-sidebar {
    width: 100%;
    height: 200px;
    border-right: none;
    border-bottom: 1px solid #e4e7ed;
  }

  .memo-editor {
    height: calc(100vh - 260px);
  }
}
</style>